import pandas as pd
from pathlib import Path

# Rutas
interim_path = Path("data/interim")
processed_path = Path("data/processed")
merged_path = processed_path / "merged"
merged_path.mkdir(parents=True, exist_ok=True)

def normalizar_texto(txt):
    if pd.isna(txt):
        return ""
    return str(txt).strip().lower().replace("á", "a").replace("é", "e") \
                                   .replace("í", "i").replace("ó", "o").replace("ú", "u")

for year in range(2017, 2026):
    print(f"\n🔄 Fusionando datos para temporada {year}/{year+1}...")

    fbref_file = processed_path / f"fbref_laliga_{year}_clean.csv"
    tm_file = interim_path / f"jugadores_laliga_{year}.csv"

    if not fbref_file.exists() or not tm_file.exists():
        print(f"⚠️ Archivos faltantes para {year}, saltando...")
        continue

    # Cargar datos
    fbref = pd.read_csv(fbref_file)
    tm = pd.read_csv(tm_file)

    # Normalizar nombre de jugador
    fbref["Player_norm"] = fbref["Player"].apply(normalizar_texto)
    tm["player_norm"] = tm["player"].apply(normalizar_texto)

    # Eliminar columnas duplicadas que ya están en FBref
    columnas_a_quitar = ["player", "age", "nationality", "season"]
    tm = tm.drop(columns=[col for col in columnas_a_quitar if col in tm.columns], errors="ignore")

    # Hacer merge SOLO por nombre normalizado
    merged = pd.merge(
        fbref, tm,
        left_on="Player_norm",
        right_on="player_norm",
        how="inner",  # left para mantener todos los jugadores de FBref
        suffixes=('', '_tm')
    )

    print(f"✅ Jugadores totales tras merge: {merged.shape[0]}")

    columnas_a_eliminar = ["Pos", "Team"]
    merged = merged.drop(columns=[col for col in columnas_a_eliminar if col in merged.columns], errors="ignore")

    # Reordenar columnas principales
    columnas_principales = [
        "Player", "position", "Age", "Nation", "Team", "club", "mv_millions", "Season", "player_url"
    ]
    columnas_auxiliares = ["Player_norm", "player_norm"]
    otras_columnas = [col for col in merged.columns if col not in columnas_principales + columnas_auxiliares]

    # Algunas columnas pueden no existir, por seguridad usamos .get
    final_df = merged[[col for col in columnas_principales if col in merged.columns] + otras_columnas]

    # Guardar
    output_file = merged_path / f"merged_laliga_{year}.csv"
    final_df.to_csv(output_file, index=False)
    print(f"💾 Guardado: {output_file.name}")
