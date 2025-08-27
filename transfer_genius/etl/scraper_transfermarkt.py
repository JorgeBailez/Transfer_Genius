import requests
import pathlib
import pandas as pd
import time
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

from transfer_genius.utils.config import load_config

# Temporadas se obtendrán dinámicamente del archivo de configuración.  La lista
# ``TEMPORADAS`` queda como valor por defecto para compatibilidad retro.  Si
# se ejecuta este módulo directamente, se cargará la configuración y se
# sobreescribirá.
TEMPORADAS = list(range(2017, 2026))  # De 2017/18 a 2025/26

# Función robusta para descargar HTML
def download_html_safe(url: str, path: pathlib.Path, retries=3, delay=10):
    if path.exists():
        print(f"⏭️ Ya existe {path.name}, se omite descarga")
        return

    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60)
            resp.raise_for_status()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(resp.content)
            print(f"✅ HTML guardado en {path} ({len(resp.content)/1024:.1f} KB)")
            return
        except Exception as e:
            print(f"⚠️ Intento {attempt+1} fallido al descargar {url}: {e}")
            time.sleep(delay)
    print(f"❌ No se pudo descargar {url} tras {retries} intentos")


def get_club_list(html_path: pathlib.Path):
    soup = BeautifulSoup(html_path.read_bytes(), "lxml")
    table = soup.select_one("table.items")
    club_links = table.select("td.hauptlink a")

    clubs = []
    for a in club_links:
        club_name = a.get("title", "").strip()
        club_href = a.get("href", "").strip()
        if club_name and "/startseite/verein/" in club_href:
            full_url = f"https://www.transfermarkt.com{club_href}"
            clubs.append({
                "club_name": club_name,
                "club_url": full_url
            })

    return clubs


def download_club_html(club: dict, path: pathlib.Path):
    if path.exists():
        print(f"⏭️ Ya existe plantilla de {club['club_name']}")
        return

    url = club["club_url"] + "/kader"
    download_html_safe(url, path)


def parse_club_table(path: pathlib.Path, club_name: str) -> pd.DataFrame:
    df_raw = pd.read_html(path, flavor="lxml")[1]
    df_raw = df_raw[['#', 'Player', 'Date of birth/Age', 'Nat.', 'Market value']].copy()

    df_raw.rename(columns={
        "Player": "player",
        "Date of birth/Age": "age",
        "Market value": "market_value"
    }, inplace=True)

    df_raw.reset_index(drop=True, inplace=True)

    soup = BeautifulSoup(path.read_bytes(), "lxml")
    table = soup.select_one("table.items")
    html_rows = table.select("tbody > tr")

    rows = []
    html_idx = 0

    for i in range(0, len(df_raw) - 2, 3):
        try:
            row_main = df_raw.loc[i]
            row_name = df_raw.loc[i + 1]
            row_pos = df_raw.loc[i + 2]

            player = str(row_name["player"]).strip()
            position = str(row_pos["player"]).strip()
            mv = row_main["market_value"]

            while html_idx < len(html_rows):
                html_tr = html_rows[html_idx]
                html_idx += 1

                player_tag = html_tr.select_one("td.hauptlink a")
                if player_tag and player_tag.text.strip() == player:
                    break
            else:
                continue

            age_cell = html_tr.select_one("td:nth-child(3)")
            age = None
            if age_cell:
                age_txt = age_cell.text.strip()
                if "(" in age_txt:
                    try:
                        age = int(age_txt.split("(")[1].replace(")", ""))
                    except:
                        age = None

            nat_imgs = html_tr.select("td:nth-child(4) img")
            nationalities = [img.get("title", "").strip() for img in nat_imgs]

            href = player_tag.get("href", "").strip()
            player_url = f"https://www.transfermarkt.com{href}" if href else ""

            jugador = {
                "player": player,
                "position": position,
                "age": age,
                "market_value": mv,
                "club": club_name,
                "nationality": nationalities,
                "player_url": player_url
            }
            rows.append(jugador)

        except Exception as e:
            print(f"❌ Error en fila {i}: {e}")
            continue

    df = pd.DataFrame(rows)

    def parse_market_value(x):
        try:
            x = x.replace("€", "").replace("-", "0").strip()
            if "m" in x:
                return float(x.replace("m", ""))
            elif "Th." in x or "k" in x:
                return float(x.replace("Th.", "").replace("k", "")) / 1000
            else:
                return 0.0
        except:
            return 0.0

    if "market_value" in df.columns:
        df["mv_millions"] = df["market_value"].apply(parse_market_value)

    return df


def scrape_transfermarkt(seasons: list[int]) -> None:
    """Descargar y procesar plantillas de La Liga para las temporadas indicadas.

    Este método se encarga de iterar sobre las temporadas proporcionadas,
    descargar la página principal de la temporada (lista de clubes),
    obtener las plantillas de cada club y guardar los CSV intermedios en
    ``data/interim``.

    Parameters
    ----------
    seasons: list[int]
        Lista de años de inicio de temporada (por ejemplo, 2017 para la
        temporada 2017/18).
    """
    for temporada in seasons:
        print(f"\n📅 Procesando temporada {temporada}/{str(temporada+1)[-2:]}...")
        url_temporada = (
            f"https://www.transfermarkt.com/laliga/startseite/wettbewerb/ES1/plus/?saison_id={temporada}"
        )
        out_path_temp = pathlib.Path(f"data/raw/tm_laliga_{temporada}/clubs.html")
        download_html_safe(url_temporada, out_path_temp)

        clubs = get_club_list(out_path_temp)
        print(f"✅ {len(clubs)} clubes encontrados para {temporada}")

        all_players_temp: list[pd.DataFrame] = []
        for club in clubs:
            name = club["club_name"]
            club_filename = f"plantilla_{name.lower().replace(' ', '_')}.html"
            club_path = pathlib.Path(f"data/raw/tm_laliga_{temporada}") / club_filename
            download_club_html(club, club_path)
            try:
                df_club = parse_club_table(club_path, name)
                df_club["season"] = f"{temporada}/{str(temporada+1)[-2:]}"
                all_players_temp.append(df_club)
            except Exception as e:
                print(f"❌ Error procesando {name} ({temporada}): {e}")

        if all_players_temp:
            df_temp = pd.concat(all_players_temp, ignore_index=True)
            out_csv = pathlib.Path(f"data/interim/jugadores_laliga_{temporada}.csv")
            out_csv.parent.mkdir(parents=True, exist_ok=True)
            df_temp.to_csv(out_csv, index=False)
            print(f"💾 Guardado {out_csv.name} ({len(df_temp)} jugadores)")
        time.sleep(1)  # reducir tiempo de espera por defecto


def main() -> None:
    """Entry point para ejecución vía ``python -m transfer_genius.etl.scraper_transfermarkt``.

    Carga la configuración desde ``configs/settings.yaml`` y ejecuta
    ``scrape_transfermarkt`` con la lista de temporadas especificada.
    """
    config = load_config()
    seasons = config.get("seasons", TEMPORADAS)
    # Asegurar que seasons es una lista de enteros
    seasons = [int(s) for s in seasons]
    scrape_transfermarkt(seasons)


if __name__ == "__main__":
    main()
