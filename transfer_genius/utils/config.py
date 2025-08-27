"""Utility functions for loading and handling configuration files.

The ETL and data processing pipelines rely on a YAML configuration file
(`configs/settings.yaml`) to specify parameters such as the seasons to
process, timeouts and caching behaviour.  Loading configuration via a
dedicated helper centralises parsing logic and makes it easy to extend
defaults in future iterations.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml  # type: ignore[import]
except ImportError:
    yaml = None  # type: ignore[assignment]

DEFAULT_CONFIG = {
    "seasons": list(range(2017, 2026)),
    "mode": "cache",  # "real" or "cache"
    "retries": 3,
    "delay": 10,
    "timeout": 30,
}


def load_config(path: str | Path = "configs/settings.yaml") -> Dict[str, Any]:
    """Load configuration from a YAML file, falling back to defaults.

    Parameters
    ----------
    path: str | Path
        Path to the YAML configuration file.  Relative paths are
        interpreted relative to the repository root.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing configuration values.  If the file
        cannot be read or parsed, ``DEFAULT_CONFIG`` is returned.
    """
    path_obj = Path(path)
    user_conf: Dict[str, Any] = {}
    if path_obj.exists():
        try:
            with open(path_obj, "r", encoding="utf-8") as f:
                content = f.read()
            if yaml is not None:
                user_conf = yaml.safe_load(content) or {}
            else:
                # Fallback simple parser: expect key: value or lists under key
                lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
                temp: Dict[str, Any] = {}
                current_key = None
                current_list: List[Any] | None = None
                for line in lines:
                    if line.startswith("-"):  # part of list
                        if current_key is not None:
                            if current_list is None:
                                current_list = []
                                temp[current_key] = current_list
                            current_list.append(line.lstrip("- "))
                    elif ":" in line:
                        key, val = [p.strip() for p in line.split(":", 1)]
                        if val:
                            temp[key] = val
                            current_key = key
                            current_list = None
                        else:
                            temp[key] = []
                            current_key = key
                            current_list = []
                user_conf = temp
        except Exception as e:
            print(f"⚠️  No se pudo cargar configuración de {path}: {e}")
            user_conf = {}
    # Convert seasons strings to ints if necessary
    seasons = user_conf.get("seasons")
    if seasons is not None and isinstance(seasons, list):
        try:
            user_conf["seasons"] = [int(x) for x in seasons]
        except ValueError:
            pass
    config = {**DEFAULT_CONFIG, **user_conf}
    return config