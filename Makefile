PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip

.PHONY: setup test lint run-app smoke clean

setup:
	@echo "Creating virtual environment and installing dependencies..."
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

test:
	@echo "Running unit tests..."
	$(VENV)/bin/pytest -q

lint:
	@echo "Running code quality checks (ruff, black, mypy)..."
	$(VENV)/bin/ruff check .
	$(VENV)/bin/black --check .
	$(VENV)/bin/mypy .

run-app:
	@echo "Launching Streamlit app..."
	$(VENV)/bin/streamlit run transfer_genius/app/main.py

smoke:
	@echo "Running smoke tests..."
	$(VENV)/bin/pytest -q -m smoke

clean:

# --- ETL Pipeline Commands ---

fetch:
	@echo "Descargando datos desde Transfermarkt y FBref según settings.yaml..."
	$(VENV)/bin/python -m transfer_genius.etl.fetch

clean-data:
	@echo "Limpieza de datos FBref"
	$(VENV)/bin/python -m transfer_genius.data.clean_fbref

merge:
	@echo "Fusionando datos Transfermarkt + FBref por temporada"
	$(VENV)/bin/python -m transfer_genius.data.merge_transfer_fbref

build-final:
	@echo "Construyendo dataset longitudinal final"
	$(VENV)/bin/python -m transfer_genius.data.merge_final

eda:
	@echo "Ejecutando notebook EDA (01_eda_core.ipynb)"
	# Nota: Dependiendo del entorno, puedes usar nbconvert o abrir manualmente.
	# Aquí se ejecuta nbconvert para generar la salida del notebook.
	$(VENV)/bin/python -m pip install --quiet nbformat nbconvert
	$(VENV)/bin/jupyter nbconvert --to notebook --execute notebooks/01_eda_core.ipynb --output notebooks/01_eda_core_out.ipynb
	@echo "Removing virtual environment and __pycache__..."
	rm -rf $(VENV)
	find . -name '__pycache__' -type d -exec rm -rf {} +