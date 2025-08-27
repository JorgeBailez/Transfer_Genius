"""
Smoke tests for the scraper components.  These tests are not meant to
fully exercise the scraping logic against the live Transfermarkt/FBref
websites; instead they act as quick checks that functions can be
imported and run without performing network I/O.  By marking these
tests with the ``smoke`` keyword we make it easy to run them on a
scheduled basis via CI to detect gross regressions.
"""
from __future__ import annotations

import pathlib
import pytest

from transfer_genius.etl.scraper_transfermarkt import download_html_safe


@pytest.mark.smoke
def test_download_html_safe_skips_existing_file(tmp_path: pathlib.Path) -> None:
    """If the output file already exists the function should not attempt to fetch it.

    This test constructs a temporary file containing dummy HTML content and
    then calls ``download_html_safe``.  Because the file exists the
    function should return immediately without raising any exceptions.
    """
    test_file = tmp_path / "dummy.html"
    test_file.write_text("<html><body>dummy</body></html>")
    # Should return quickly and not modify the file
    download_html_safe("http://example.com", test_file)
    assert test_file.exists()
    assert test_file.read_text() == "<html><body>dummy</body></html>"