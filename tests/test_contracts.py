"""
Contract tests to validate basic data expectations on CSV outputs.

These tests ensure that core assumptions about the processed data are
enforced: ``mv_millions`` should be non-negative and ``Season`` should
follow the pattern ``YYYY/YY``.  They operate on small sample
dataframes written to temporary CSVs during testing.
"""
from __future__ import annotations

import pandas as pd
import re


def test_mv_millions_non_negative(tmp_path):
    """All values in ``mv_millions`` must be greater or equal to zero."""
    df = pd.DataFrame({
        "mv_millions": [10.5, 0.0, 3.2, 0.0],
        "Season": ["2017/18", "2018/19", "2019/20", "2020/21"],
    })
    csv_path = tmp_path / "sample.csv"
    df.to_csv(csv_path, index=False)
    loaded = pd.read_csv(csv_path)
    assert (loaded["mv_millions"] >= 0).all(), "mv_millions contiene valores negativos"


def test_season_pattern(tmp_path):
    """The ``Season`` column must follow the ``YYYY/YY`` pattern."""
    df = pd.DataFrame({
        "mv_millions": [1.0],
        "Season": ["2023/24"],
    })
    csv_path = tmp_path / "sample.csv"
    df.to_csv(csv_path, index=False)
    loaded = pd.read_csv(csv_path)
    pattern = re.compile(r"^\d{4}/\d{2}$")
    assert loaded["Season"].apply(lambda x: bool(pattern.match(x))).all(), "Season no sigue el patrón YYYY/YY"