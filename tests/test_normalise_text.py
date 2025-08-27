"""
Tests for the text normalisation helper used during dataset merging.

``merge_transfer_fbref.py`` defines a small helper called
``normalizar_texto`` which strips accents, lowers case and removes
extraneous whitespace.  Accurate normalisation is vital when joining
records from FBref and Transfermarkt which may have slight differences
in naming conventions.  These tests ensure the helper performs the
expected transformations.
"""
from __future__ import annotations

import pytest

from transfer_genius.data.merge_transfer_fbref import normalizar_texto


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("Álvaro García", "alvaro garcia"),
        ("Éric Abidal", "eric abidal"),
        ("Óscar de Marcos", "oscar de marcos"),
        ("José María", "jose maria"),
        (None, ""),
    ],
)
def test_normalizar_texto_removes_accents_and_lowercases(input_text: str | None, expected: str) -> None:
    """Ensure accents are removed, text lowercased and None yields empty string."""
    assert normalizar_texto(input_text) == expected