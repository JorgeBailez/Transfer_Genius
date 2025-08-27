"""Script de alto nivel para descargar datos de Transfermarkt y FBref.

Este módulo se encarga de orquestar la descarga de datos para ambas
fuentes en función de la configuración especificada en
``configs/settings.yaml``.  Si el modo está en ``cache``, sólo se
descargarán los datos que no existan en disco.  Si está en ``real`` se
forzará la descarga de todas las temporadas, sobrescribiendo los
archivos existentes.
"""
from __future__ import annotations

from pathlib import Path

from transfer_genius.utils.config import load_config
from transfer_genius.etl.scraper_transfermarkt import scrape_transfermarkt
from transfer_genius.etl.scraper_fbref import scrape_fbref


def main() -> None:
    config = load_config()
    seasons = [int(s) for s in config.get("seasons", [])]
    mode = config.get("mode", "cache")
    # Si modo es real, se borra la carpeta data/raw y data/interim para forzar descarga
    if mode == "real":
        for subdir in ["data/raw", "data/interim"]:
            path = Path(subdir)
            if path.exists():
                print(f"🗑️  Modo real: eliminando {path} para recargar datos...")
                for child in path.rglob("*"):
                    if child.is_file():
                        child.unlink()
    # Ejecutar scrapers
    if seasons:
        print(f"🛰️  Iniciando descarga para temporadas: {seasons}")
        scrape_transfermarkt(seasons)
        scrape_fbref(seasons)
    else:
        print("⚠️  No hay temporadas definidas en la configuración.")


if __name__ == "__main__":
    main()