import pandas as pd
from pathlib import Path

# Carpeta de entrada con los merged_laliga_20XX.csv
merged_path = Path("data/processed/merged")
output_path = Path("data/final")
output_path.mkdir(parents=True, exist_ok=True)  # ✅ Crear carpeta si no existe

# Leer todos los CSV de merged
archivos = sorted(merged_path.glob("merged_laliga_20*.csv"))

dfs = []
for archivo in archivos:
    print(f"📥 Leyendo {archivo.name}")
    df = pd.read_csv(archivo)
    dfs.append(df)

# Concatenar todos los DataFrames
df_final = pd.concat(dfs, ignore_index=True)

# Guardar resultado combinado
output_file = output_path / "fbref_tm_laliga_longitudinal.csv"
df_final.to_csv(output_file, index=False)
print(f"\n✅ Dataset longitudinal guardado en {output_file}")
