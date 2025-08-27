"""
Smoke test to ensure that all high-level modules can be imported without
raising exceptions.  This acts as a quick check to detect syntax
errors or missing dependencies before deeper tests run.
"""
from __future__ import annotations

import importlib
import pytest


@pytest.mark.smoke
@pytest.mark.parametrize(
    "module_name",
    [
        "transfer_genius.etl.scraper_transfermarkt",
        "transfer_genius.etl.scraper_fbref",
        "transfer_genius.etl.fetch",
        "transfer_genius.data.clean_fbref",
        "transfer_genius.data.merge_transfer_fbref",
        "transfer_genius.data.merge_final",
    ],
)
def test_module_imports(module_name):
    """Import modules and assert that they don't raise ImportError."""
    importlib.import_module(module_name)