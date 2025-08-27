# Informe de Auditoría – Transfer Genius

Este informe documenta los hallazgos y las acciones tomadas durante la
auditoría inicial del repositorio **Transfer Genius** realizada en la
rama `chore/audit-transfer-genius`.

## Inventario inicial

Antes de la auditoría el repositorio contenía únicamente unos pocos
scripts sueltos y notebooks:

- `hola.py`: script de scraping de valores de mercado de la temporada
  actual de La Liga.
- `src/scraper_transfermarkt.py`: scrapper de plantillas de clubs de
  Transfermarkt por temporadas.
- `src/scraper_fbref.py`: scrapper de estadísticas de FBref (no
  ejecutado en esta auditoría).
- `src/limpieza_fbref_laliga_20XX.py`: función para limpiar datos de
  FBref.
- `src/merge_transfer_fbref.py`: unión de datos de FBref y
  Transfermarkt.
- `src/merge_final.py`: concatenación de temporadas fusionadas.
- Cuadernos Jupyter en `EDA/` y algunos archivos temporales.
- Un `README.md` minimal con solo el título y sin instrucciones.
- Ausencia de ficheros de dependencias (`requirements.txt` o
  `pyproject.toml`), tests, workflows de CI o estructura de paquete.

## Principales deficiencias detectadas

1. **Falta de estructura de paquete**: el código Python no estaba
   organizado como módulo instalable, lo que dificulta el uso y
   testeo.
2. **Ausencia de gestión de dependencias**: no había ni
   `requirements.txt` ni `pyproject.toml`, por lo que reproducir
   el entorno era impreciso.
3. **Ausencia de tests**: el repositorio carecía de pruebas unitarias y
   de humo que garanticen el correcto funcionamiento tras cambios.
4. **Documentación mínima**: el `README.md` no explicaba cómo utilizar
   los scripts ni reproducir el pipeline; tampoco había un diccionario
   de datos.
5. **Sin CI/CD**: no existía ningún flujo de integración continua para
   ejecutar linters y tests en cada cambio.

## Acciones realizadas

Durante la auditoría se llevaron a cabo las siguientes tareas para
subsanar las deficiencias detectadas:

1. **Reestructuración del proyecto** en un paquete llamado
   `transfer_genius` con los submódulos `etl`, `data`, `app` y
   `utils`.  Se añadieron ficheros `__init__.py` para hacerlo
   instalable y se movieron los scripts originales a rutas más
   descriptivas (por ejemplo, `hola.py` pasó a
   `transfer_genius/etl/scraper_marketvalues.py`).
2. **Creación de un `requirements.txt` y `pyproject.toml`** que
   enumeran todas las dependencias principales (pandas, numpy,
   requests, bs4, lxml, pytest, ruff, black, mypy, etc.) y configuran
   las herramientas de formato y análisis estático.
3. **Implantación de un conjunto de pruebas** en el directorio
   `tests/`.  Se añadieron tests unitarios para las funciones de
   limpieza de FBref y la normalización de nombres, así como un test de
   humo para los scrapers.  Esto sienta las bases para aumentar la
   cobertura en el futuro.
4. **Introducción de un `Makefile`** con tareas para instalar el
   entorno, ejecutar tests, linters y lanzar la aplicación Streamlit.
5. **Configuración de CI con GitHub Actions** en
   `.github/workflows/ci.yml`.  El workflow ejecuta linters, tests y
   programa pruebas de humo diarias.  Se añadieron
   **badges** en el README para reflejar el estado de la última
   ejecución.
6. **Actualización de la documentación**.  Se sustituyó el antiguo
   README por uno completo que explica la estructura del proyecto, cómo
   instalarlo, reproducir el pipeline y contribuir.  Se creó un
   `DATA_DICTIONARY.md` que explica cada columna del dataset resultante
   y un `CONTRIBUTING.md` con las normas de colaboración.
7. **Plantilla de Pull Request**.  Se añadió un
   `.github/PULL_REQUEST_TEMPLATE.md` para guiar a los colaboradores en
   la descripción y checklist de sus cambios.

## Pendientes y recomendaciones

* **Completar los módulos `app` y `utils`**: de momento son
  contenedores vacíos.  Será necesario implementar la app Streamlit y
  factorizar utilidades comunes.
* **Añadir más pruebas**: los scrapers no están cubiertos en su
  totalidad.  Se deberían emplear técnicas de mocking o fixtures
  controlados para verificar que los parseos funcionan correctamente.
* **Validaciones de datos**: implementar reglas de calidad usando
  frameworks como `great_expectations` para cada etapa del pipeline.
* **Optimización de rendimiento**: explorar el uso de peticiones en
  paralelo y procesamiento vectorizado en pandas o polars.
* **Despliegue continuo**: agregar un workflow que
  construya y publique artefactos (p. ej. el dataset final) o despliegue
  la aplicación.

## Conclusión

La auditoría inicial de Transfer Genius revela un proyecto en fase muy
temprana pero con gran potencial.  El trabajo realizado establece una
base sólida para evolucionar hacia un pipeline de datos robusto y
profesional, con buenas prácticas de desarrollo, reproducibilidad y
mantenibilidad.  Se anima a seguir iterando sobre las recomendaciones
pendientes y a ampliar la cobertura de pruebas conforme avance el
desarrollo.