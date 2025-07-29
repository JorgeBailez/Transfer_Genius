import requests
from bs4 import BeautifulSoup
import pandas as pd
import pathlib
import time

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}

BASE_URL = "https://www.transfermarkt.com/laliga/marktwerte/wettbewerb/ES1"
RAW_DIR = pathlib.Path("data/raw")
OUT_CSV = pathlib.Path("data/processed/marketvalues_laliga_2024.csv")



def download_all_pages(base_url: str, pages: int, save_dir: pathlib.Path) -> list[pathlib.Path]:
    save_dir.mkdir(parents=True, exist_ok=True)
    html_paths = []

    for page in range(1, pages + 1):
        url = base_url if page == 1 else f"{base_url}/page/{page}"
        file = save_dir / f"transfermarkt_laliga_p{page}.html"

        if not file.exists():
            print(f"📥 Descargando página {page}...")
            resp = requests.get(url, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            file.write_bytes(resp.content)
        else:
            print(f"✔ Página {page} ya descargada.")

        html_paths.append(file)

    return html_paths

def parse_table(path: pathlib.Path) -> pd.DataFrame:
    df_raw = pd.read_html(path, flavor="lxml")[1]
    df_raw = df_raw[['#', 'Player', 'Age', 'Market value']].copy()
    df_raw.reset_index(drop=True, inplace=True)

    soup = BeautifulSoup(path.read_bytes(), "lxml")
    table = soup.select_one("table.items")
    html_rows = table.select("tbody > tr")

    rows = []
    html_idx = 0
    for i in range(0, len(df_raw) - 2, 3):
        try:
            row_main = df_raw.loc[i]
            row_name = df_raw.loc[i+1]
            row_pos  = df_raw.loc[i+2]

            player = str(row_name["Player"]).strip()
            position = str(row_pos["Player"]).strip()
            age = row_main["Age"]
            mv = row_main["Market value"]

            while html_idx < len(html_rows):
                html_tr = html_rows[html_idx]
                html_idx += 1

                player_tag = html_tr.select_one("td:nth-child(2) a")
                if player_tag and player_tag.get("title", "").strip() == player:
                    break
            else:
                continue

            club_img = html_tr.select_one("td:nth-child(5) img")
            club = club_img.get("alt", "").strip() if club_img else ""

            nat_imgs = html_tr.select("td:nth-child(3) img")
            nationalities = [img.get("title", "").strip() for img in nat_imgs]

            href = player_tag.get("href", "").strip()
            player_url = f"https://www.transfermarkt.com{href}" if href else ""

            rows.append({
                "player": player,
                "position": position,
                "age": age,
                "market_value": mv,
                "club": club,
                "nationality": nationalities,
                "player_url": player_url
            })
        except Exception as e:
            print(f"❌ Error en fila {i}: {e}")
            continue

    df = pd.DataFrame(rows)

    def parse_market_value(x):
        try:
            x = x.replace("€", "").replace("-", "0").strip()
            if "m" in x:
                return float(x.replace("m", ""))
            elif "Th." in x:
                return float(x.replace("Th.", "")) / 1000
            else:
                return 0.0
        except:
            return 0.0

    df["mv_millions"] = df["market_value"].apply(parse_market_value)
    print(f"🔍 {path.name} → {len(df)} jugadores")
    return df

def parse_multiple_tables(paths: list[pathlib.Path]) -> pd.DataFrame:
    all_rows = []
    for path in paths:
        df = parse_table(path)
        all_rows.append(df)
    return pd.concat(all_rows, ignore_index=True)


if __name__ == "__main__":
    t0 = time.perf_counter()

    html_paths = download_all_pages(BASE_URL, pages=4, save_dir=RAW_DIR)
    df_mv = parse_multiple_tables(html_paths)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_mv.to_csv(OUT_CSV, index=False)

    print(f"✓ CSV limpio → {OUT_CSV} ({len(df_mv)} jugadores)")
    print(f"⏱️  Todo listo en {time.perf_counter()-t0:.1f}s")
