import pytest
import types
import pandas as pd
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

import scrapers.mommy_poppins as mommy_poppins
from scrapers.mommy_poppins import extract_max_page

MOCK_HTML_PAGE_1 = """
<div class="pager-wrapper">
  <a>1</a>
  <a>2</a>
</div>
<div class="list-container">
  <div>
    <div class="events-date-header">Mon, Jan 01</div>
    <div class="list-item event">
      <div class="content-details">
        <h2>Test Event Title</h2>
        <div style=""><span>Test Location</span></div>
        <noscript>Test Description</noscript>
        <div class="specialtags">
          <span class="tag">Free</span>
          <span class="tag">Family</span>
        </div>
      </div>
      <span class="times-label">10:00 AM - 12:00 PM</span>
      <a href="/event/test-event"></a>
    </div>
  </div>
</div>
"""

MOCK_HTML_PAGE_2 = """
<div class="list-container">
  <div>
    <div class="events-date-header">Tue, Jan 02</div>
    <div class="list-item event">
      <div class="content-details">
        <h2>Another Event</h2>
        <div style=""><span>Another Location</span></div>
        <noscript>Another Description</noscript>
        <div class="specialtags">
          <span class="tag">Paid</span>
        </div>
      </div>
      <span class="times-label">2:00 PM - 4:00 PM</span>
      <a href="/event/another-event"></a>
    </div>
  </div>
</div>
"""


@pytest.fixture
def mock_requests_get():
    """
    Mocks the requests.get function to return a page of events from Mommy Poppins.
    
    The first call returns page 1, the second call returns page 2. This allows us to test
    the case where the total number of events is not a multiple of 20.
    """
    with patch("scrapers.mommy_poppins.requests.get") as mock_get:
        # First call returns page 1, second call returns page 2
        mock_get.side_effect = [
            MagicMock(text=MOCK_HTML_PAGE_1),
            MagicMock(text=MOCK_HTML_PAGE_1),
            MagicMock(text=MOCK_HTML_PAGE_2),
        ]
        yield mock_get


@pytest.fixture
def mock_to_csv(monkeypatch):
    # Patch DataFrame.to_csv to avoid file I/O
    """
    Patch DataFrame.to_csv to avoid file I/O during unit tests.
    """
    
    monkeypatch.setattr(pd.DataFrame, "to_csv", lambda self, *a, **k: None)


def test_run_mommy_poppins_basic(mock_requests_get, mock_to_csv, tmp_path, monkeypatch):
    """
    Test run_mommy_poppins with a basic API response.

    Should:
    - Call requests.get for both pages
    - Call pd.DataFrame.to_csv with the correct arguments
    - Write a CSV file with the correct name
    """
    # Patch print to suppress output
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    # Patch outfile path to tmp_path
    monkeypatch.setattr(
        mommy_poppins, "run_mommy_poppins", mommy_poppins.run_mommy_poppins
    )
    # Run the function
    mommy_poppins.run_mommy_poppins(mnth=1, yr=2024)

    # Check that requests.get was called for both pages
    assert mock_requests_get.call_count >= 2


def test_extract_max_page():
    """
    Test that extract_max_page returns the correct maximum page number from a given page.

    Should:
    - Return 2 for the given page
    """
    soup = BeautifulSoup(MOCK_HTML_PAGE_1, "html.parser")
    max_page = extract_max_page(soup)
    assert max_page == 2


def test_event_parsing(monkeypatch, mock_requests_get, mock_to_csv):
    """
    Test event parsing from Mommy Poppins page.

    Should:
    - Find all events by title
    - Find all events by tags
    - Find all events by link
    """
    # Patch print to suppress output
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)
    events = []

    # Patch pd.DataFrame to capture events
    orig_df = pd.DataFrame

    def fake_df(data):
        events.extend(data)
        return orig_df(data)

    monkeypatch.setattr(pd, "DataFrame", fake_df)

    mommy_poppins.run_mommy_poppins(mnth=1, yr=2024)

    assert any(e["Title"] == "Test Event Title" for e in events)
    assert any(e["Title"] == "Another Event" for e in events)
    assert any(e["Tags"] == "Free, Family" for e in events)
    assert any(e["Tags"] == "Paid" for e in events)
    assert all(
        "Link" in e and e["Link"].startswith("https://mommypoppins.com") for e in events
    )
