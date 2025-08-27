# Transfer Genius

Transfer Genius es un proyecto de ciencia de datos que construye una visión
longitudinal de los jugadores de La Liga a partir de dos fuentes
principales: **FBref** (estadísticas deportivas) y **Transfermarkt**
(valores de mercado y plantillas).  El objetivo último es disponer de un
dataset listo para modelizar la revalorización futura de jugadores y
facilitar un cuadro de mando exploratorio con Streamlit.

## Estructura del repositorio

El código se organiza como un paquete de Python instalable en
`transfer_genius/` y varios submódulos:

```
transfer_genius/
  etl/              # Scripts de scraping y extracción de datos brutos
  data/             # Limpieza, validación y fusión de datasets
  app/              # Aplicación Streamlit (por implementar)
  utils/            # Funciones de apoyo reutilizables
notebooks/          # Cuadernos de exploración EDA (no ejecutados en CI)
tests/              # Pruebas unitarias y de humos (pytest)
configs/            # Configuraciones para linters y herramientas
scripts/            # Tareas auxiliares (ej. CLI futuro)
.github/workflows/  # Workflows de CI para lint, tests y humos programados
Makefile           # Comandos de conveniencia (setup, test, lint, run-app)
requirements.txt   # Dependencias de Python fijadas
pyproject.toml     # Configuración de black, ruff y mypy
configs/settings.yaml # Parámetros de scraping (temporadas, modo cache/real, etc.)
```

## Instalación y entorno

Se recomienda crear un entorno virtual antes de instalar las dependencias.
Puedes usar el **Makefile** incluido para automatizar el proceso:

```bash
# Crear entorno virtual e instalar dependencias
make setup

# Ejecutar las pruebas unitarias
make test

# Ejecutar comprobaciones de calidad de código (ruff, black, mypy)
make lint

# Lanzar la aplicación Streamlit (cuando exista)
make run-app

# Ejecutar solo las pruebas de humo (rápidas) — utilizadas por CI nocturno
make smoke
```

Si prefieres instalar manualmente sin Makefile:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pytest
```

## Cómo reproducir la canalización de datos

Para reproducir de forma automática todos los pasos de descarga,
limpieza, merge y generación del dataset final utiliza los comandos
definidos en el Makefile.  El fichero de configuración
`configs/settings.yaml` controla las temporadas a procesar y si el modo
es "real" (descarga forzada) o "cache" (sólo descarga si no existe):

1. **Descarga de datos**: Descarga las páginas de Transfermarkt y FBref
   para las temporadas indicadas.  Usa caché cuando sea posible.
   ```bash
   make fetch
   ```
   Esto almacenará los HTML y CSV intermedios en `data/raw/` y
   `data/interim/`.

2. **Limpieza de datos FBref**: Limpia los CSV de FBref generados o
   que hayas copiado manualmente en `data/interim/`.
   ```bash
   make clean-data
   ```
   Se generan ficheros `fbref_laliga_20xx_clean.csv` en
   `data/processed/`.

3. **Merge FBref + Transfermarkt**: Fusiona los datos limpios de FBref
   con los CSV de jugadores de Transfermarkt por temporada.
   ```bash
   make merge
   ```
   Este paso crea `merged_laliga_20xx.csv` en `data/processed/merged/` y
   muestra en consola el número de jugadores emparejados.

4. **Dataset longitudinal final**: Concatena todas las temporadas
   fusionadas en un único dataset.
   ```bash
   make build-final
   ```
   El resultado se guarda en `data/final/fbref_tm_laliga_longitudinal.csv`.

5. **Análisis exploratorio (EDA)**: Ejecuta el notebook principal de
   análisis (`notebooks/01_eda_core.ipynb`) para obtener al menos 10
   insights sobre el dataset.
   ```bash
   make eda
   ```
   El comando generará un notebook ejecutado en
   `notebooks/01_eda_core_out.ipynb`.

## Calidad de código y pruebas

Este proyecto utiliza **pytest** para las pruebas unitarias y de humo.
Las pruebas unitarias se encuentran en `tests/` e incluyen verificaciones
de limpieza de datos y normalización de nombres.  Las pruebas marcadas
con `@pytest.mark.smoke` son ejecuciones rápidas que garantizan que los
scrapers no fallen al iniciarse en ausencia de red o archivos.

Los linters configurados son **ruff** para estilo, **black** para
formateo automático y **mypy** para comprobación estática de tipos.  La
configuración se encuentra en `pyproject.toml`.

## Contribución

Las aportaciones son bienvenidas.  Consulta el archivo
[`CONTRIBUTING.md`](CONTRIBUTING.md) para conocer las normas de estilo,
guías de ramificación y plantillas de pull request.  Si encuentras un
bug o tienes una sugerencia, abre un issue siguiendo la plantilla.

## Licencia

Este proyecto se distribuye bajo la MIT License.