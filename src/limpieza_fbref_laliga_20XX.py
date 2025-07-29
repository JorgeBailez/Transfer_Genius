import pandas as pd
from pathlib import Path
import re

def limpiar_df_fbref(df):
    # 1. Eliminar filas de resumen como "Opponent Total", "Squad Total"
    df = df[~df["Player"].isin(["Opponent Total", "Squad Total"])]

    # 2. Eliminar duplicados exactos si existieran
    df = df.drop_duplicates()

    # 3. Eliminar columnas con todos los valores NaN
    df = df.dropna(axis=1, how='all')

    # 4. Limpiar campo Nation: quedarse solo con parte en mayúsculas (ej: "ESP")
    if "Nation" in df.columns:
        df["Nation"] = df["Nation"].astype(str).str.extract(r"([A-Z]{2,3})", expand=False)

    # 5. Arreglar formato de Season: de "2017-2018" → "2017/2018"
    if "Season" in df.columns:
        df["Season"] = df["Season"].astype(str).str.replace("-", "/", regex=False)
    else:
        df["Season"] = "desconocida"

    # 6. Rellenar Team si no está
    if "Team" not in df.columns or df["Team"].isna().all():
        df["Team"] = "desconocido"

    return df

# Carpeta con los CSV por temporada
input_dir = Path("data/interim")
output_dir = Path("data/processed")
output_dir.mkdir(parents=True, exist_ok=True)

# Procesar todos los ficheros que empiezan por fbref_laliga_20XX.csv
for file in input_dir.glob("fbref_laliga_20*.csv"):
    print(f"🧼 Limpiando {file.name}...")
    df = pd.read_csv(file)
    df_clean = limpiar_df_fbref(df)

    # Guardar versión limpia
    output_path = output_dir / file.name.replace(".csv", "_clean.csv")
    df_clean.to_csv(output_path, index=False)
    print(f"✅ Guardado limpio: {output_path.name}")

