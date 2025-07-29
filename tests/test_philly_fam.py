import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os

import scrapers.philly_fam as philly_fam

SAMPLE_ICS = """
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Sample Corp//NONSGML Event//EN
BEGIN:VEVENT
UID:1
DTSTAMP:20240601T120000Z
DTSTART:20240610T140000Z
DTEND:20240610T160000Z
SUMMARY:Sample Event
LOCATION:Sample Location
DESCRIPTION:Sample Description
CATEGORIES:Kids,Family
URL:https://example.com/event
END:VEVENT
END:VCALENDAR
"""

@patch("scrapers.philly_fam.requests.get")
@patch("scrapers.philly_fam.Calendar")
def test_run_philly_fam_creates_csv(mock_calendar, mock_get, tmp_path):
  # Mock the requests.get response
  """
  Test that run_philly_fam() creates a CSV file with the event data scraped
  from the iCalendar feed.

  This test uses the mock library to substitute the requests.get() call and
  the Calendar object with mock objects. The mock objects are configured to
  return the SAMPLE_ICS string as the response content, and the event object
  is configured with the expected event data.

  The test then calls run_philly_fam() with the mocked objects and checks that
  the CSV file is created in the expected location with the expected data.
  """
  mock_response = MagicMock()
  mock_response.headers = {"Content-Type": "text/calendar"}
  mock_response.text = SAMPLE_ICS
  mock_get.return_value = mock_response

  # Mock Calendar and its events
  mock_event = MagicMock()
  mock_event.begin.datetime = pd.Timestamp("2024-06-10 14:00")
  mock_event.end.datetime = pd.Timestamp("2024-06-10 16:00")
  mock_event.name = "Sample Event"
  mock_event.location = "Sample Location"
  mock_event.description = "Sample Description"
  mock_event.categories = ["Kids", "Family"]
  mock_event.url = "https://example.com/event"
  mock_calendar.return_value.events = [mock_event]

  philly_fam.run_philly_fam(mnth=6, yr=2024, output_dir=tmp_path)
  outfile = tmp_path / "2024_06_philly_family.csv"
  assert os.path.exists(outfile)
  df = pd.read_csv(outfile)
  assert len(df) == 1
  assert df.iloc[0]["Title"] == "Sample Event"
  assert df.iloc[0]["Location"] == "Sample Location"
  assert "Sample Description" in df.iloc[0]["Description"]
  assert "Kids" in df.iloc[0]["Tags"]
  assert "Family" in df.iloc[0]["Tags"]
  assert df.iloc[0]["Link"] == "https://example.com/event"

@patch("scrapers.philly_fam.requests.get")
def test_run_philly_fam_unexpected_content_type(mock_get):
  """
  Test that run_philly_fam() raises ValueError when the iCalendar feed has
  an unexpected Content-Type header value.

  This test uses the mock library to substitute the requests.get() call with
  a mock object that returns an HTML response instead of a calendar. The test
  then calls run_philly_fam() and checks that a ValueError is raised with the
  expected error message.
  """
  mock_response = MagicMock()
  mock_response.headers = {"Content-Type": "text/html"}
  mock_response.text = "<html>Not a calendar</html>"
  mock_get.return_value = mock_response

  with pytest.raises(ValueError, match="Expected calendar data"):
    philly_fam.run_philly_fam(mnth=6, yr=2024)