import requests
import pathlib
from bs4 import BeautifulSoup
import  pandas as pd

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

URL_CLUBS = "https://www.transfermarkt.com/laliga/daten/wettbewerb/ES1"
OUT_PATH = pathlib.Path("data/raw/transfermarkt_laliga_clubs.html")

def download_html(url: str, path: pathlib.Path) -> None:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()  # Lanza excepción si hay error HTTP
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    print(f"✅ HTML guardado en {path} ({len(resp.content)/1024:.1f} KB)")

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

    print(f"🏟️ Extraídos {len(clubs)} clubes.")
    return clubs


def download_club_html(club: dict, path: pathlib.Path):
    url = club["club_url"] + "/kader"
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(resp.content)
    print(f"✅ HTML plantilla guardado en {path} ({len(resp.content)/1024:.1f} KB)")

def parse_club_table(path: pathlib.Path, club_name: str) -> pd.DataFrame:
    # Leemos la tabla principal del club
    df_raw = pd.read_html(path, flavor="lxml")[1]
    df_raw = df_raw[['#', 'Player', 'Date of birth/Age', 'Nat.', 'Market value']].copy()

    df_raw.rename(columns={
        "Player": "player",
        "Date of birth/Age": "age",
        "Market value": "market_value"
    }, inplace=True)

    df_raw.reset_index(drop=True, inplace=True)
    print("📋 Columnas en df_raw:", df_raw.columns.tolist())
    print(df_raw.head(3))

    # Parseo adicional con BeautifulSoup
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

            # Buscar la fila HTML que coincide con el jugador (por texto visible)
            while html_idx < len(html_rows):
                html_tr = html_rows[html_idx]
                html_idx += 1

                player_tag = html_tr.select_one("td.hauptlink a")
                if player_tag and player_tag.text.strip() == player:
                    break
            else:
                print(f"⚠️ No encontrado en HTML: {player}")
                continue

            # Edad (de "May 11, 1992 (33)" → 33)
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
            print("✅ Jugador extraído:", jugador)
            rows.append(jugador)

        except Exception as e:
            print(f"❌ Error en fila {i}: {e}")
            continue

    # DataFrame final
    df = pd.DataFrame(rows)

    if len(df) == 0:
        print(f"⚠️ No se extrajo ninguna fila para {club_name}")
    else:
        print(f"📊 Columnas en df final: {df.columns.tolist()}")
        print(df.head())

    # Conversión del valor de mercado
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
    else:
        print("❌ 'market_value' no está en el DataFrame final")

    print(f"🔍 {club_name} → {len(df)} jugadores")
    return df



if __name__ == "__main__":
    # Paso 1: Descargar HTML de clubes
    download_html(URL_CLUBS, OUT_PATH)
    clubs = get_club_list(OUT_PATH)
    print("✅ Ejemplo:", clubs[0])

    all_players = []

    for club in clubs:
        try:
            name = club['club_name']
            url = club['club_url']
            print(f"\n=== 🔄 Procesando {name} ===")

            # Nombre de archivo para guardar la plantilla
            club_filename = f"plantilla_{name.lower().replace(' ', '_')}.html"
            club_path = pathlib.Path("data/raw") / club_filename

            # Descargar HTML solo si no existe (puedes quitar el if para forzar la descarga)
            if not club_path.exists():
                download_club_html(club, club_path)

            # Extraer jugadores de ese club
            df = parse_club_table(club_path, name)
            all_players.append(df)

        except Exception as e:
            print(f"❌ Error procesando {club['club_name']}: {e}")

    # Paso 3: Unir todos los DataFrames
    final_df = pd.concat(all_players, ignore_index=True)

    # Paso 4: Guardar a CSV
    OUT_CSV = pathlib.Path("data/processed/jugadores_laliga_2024.csv")
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(OUT_CSV, index=False)
    print(f"\n✅ CSV final guardado en {OUT_CSV} con {len(final_df)} jugadores")
