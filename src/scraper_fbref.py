import time
import pandas as pd
from pathlib import Path
import re

TABLAS_UTILES = [0, 2, 3, 4, 5, 7, 8, 9, 10, 11]
OUTPUT_DIR = Path("data/interim")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extraer_tablas_utiles(URL: str, indices_utiles: list[int]) -> list[pd.DataFrame]:
    tablas = pd.read_html(URL, header=[0, 1])
    print(f"📊 Tablas totales encontradas: {len(tablas)}")

    tablas_utiles = []
    for i in indices_utiles:
        df = tablas[i].copy()
        print(f"\n✅ Tabla {i} seleccionada")
        print(f"Shape: {df.shape}")
        print(f"Columnas: {df.columns.tolist()[:5]} ...")
        tablas_utiles.append(df)

    return tablas_utiles

def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    def limpiar_col(col):
        if isinstance(col, tuple):
            col = "_".join(col)
        col = re.sub(r"^Unnamed: \d+_level_\d+_", "", col)
        return col.strip()
    df.columns = [limpiar_col(col) for col in df.columns]
    return df

def limpiar_tabla(df: pd.DataFrame) -> pd.DataFrame:
    df = flatten_columns(df)
    col_player = next((col for col in df.columns if 'Player' in col), None)
    if col_player is None:
        print("⚠️ No se encontró columna de jugador.")
        return None

    df = df[~df[col_player].isin(['Player'])]
    df = df.dropna(subset=[col_player])
    df = df.rename(columns={col_player: 'Player'})

    if 'Matches' in df.columns:
        df.drop(columns='Matches', inplace=True)

    return df

def merge_controlado_por_player(tablas: list[pd.DataFrame]) -> pd.DataFrame:
    tablas_limpias = [limpiar_tabla(df) for df in tablas if df is not None]
    df_base = tablas_limpias[0]

    for i, df_nueva in enumerate(tablas_limpias[1:], start=1):
        columnas_base = set(df_base.columns)
        columnas_nueva = set(df_nueva.columns)

        columnas_duplicadas = (columnas_base & columnas_nueva) - {'Player'}
        if columnas_duplicadas:
            print(f"🔁 Paso {i}: eliminando duplicadas → {columnas_duplicadas}")
            df_nueva = df_nueva.drop(columns=columnas_duplicadas, errors='ignore')

        columnas_nuevas = set(df_nueva.columns) - columnas_base
        print(f"➕ Paso {i}: nuevas columnas añadidas → {columnas_nuevas}")

        df_base = pd.merge(df_base, df_nueva, on='Player', how='outer')

    return df_base

# === BUCLE POR TEMPORADAS ===

for year in range(2018, 2019):
    season_label = f"{year}-{year+1}"
    season_url = f"https://fbref.com/en/comps/12/{season_label}/{season_label}-La-Liga-Stats"
    output_file = OUTPUT_DIR / f"fbref_laliga_{year}.csv"

    if output_file.exists():
        print(f"⏭️ Ya existe {output_file.name}, se omite")
        continue

    try:
        print(f"\n📅 Procesando temporada {season_label} → {season_url}")
        la_liga = pd.read_html(season_url, extract_links='all')[0]

        equipos_urls = {}
        for fila in la_liga[(('Squad', None))].dropna():
            nombre_equipo, enlace = fila
            if enlace:
                equipos_urls[nombre_equipo.strip()] = f"https://fbref.com{enlace}"

        print(f"✅ Se encontraron {len(equipos_urls)} equipos")

        dfs = []
        for nombre, url in equipos_urls.items():
            print(f"\n📥 Procesando {nombre} → {url}")
            tablas_equipo = extraer_tablas_utiles(url, TABLAS_UTILES)
            df_equipo = merge_controlado_por_player(tablas_equipo)
            df_equipo["Team"] = nombre
            df_equipo["Season"] = season_label
            dfs.append(df_equipo)
            time.sleep(5)  # para evitar bloqueo

        # Concatenar temporada y guardar
        df_final_fbref = pd.concat(dfs, ignore_index=True)
        df_final_fbref.to_csv(output_file, index=False)
        print(f"✅ Guardado → {output_file.name} ({len(df_final_fbref)} filas)")

    except Exception as e:
        print(f"❌ Error en temporada {season_label}: {e}")
        continue

    time.sleep(60)  # pausa entre temporadas
