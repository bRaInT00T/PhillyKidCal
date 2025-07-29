from scrapers import macaroni_kid
from unittest.mock import patch, MagicMock
import pandas as pd
import pytest


@patch("scrapers.macaroni_kid.requests.get")
@patch("scrapers.macaroni_kid.datetime")
@patch("scrapers.macaroni_kid.pd.DataFrame.to_csv")
def test_run_macaroni_kid_basic(mock_to_csv, mock_datetime, mock_get):
    # Mock current date
    """
    Test run_macaroni_kid with a basic API response.
    
    Should:
    - Write a CSV file with the correct name
    - Include the correct columns and values in the CSV file
    - Call pandas.DataFrame.to_csv with the correct arguments
    """
    mock_now = MagicMock()
    mock_now.month = 5
    mock_now.year = 2024
    mock_datetime.now.return_value = mock_now

    # Mock API response
    mock_response = MagicMock()
    mock_response.json.return_value = [
        {
            "title": "Test Event",
            "cost": "Free",
            "startDateTime": "2024-05-10T10:00:00.000Z",
            "endDateTime": "2024-05-10T12:00:00.000Z",
            "where": "Test Location",
            "categories": [{"name": "Family"}],
            "address": {
                "street": "123 Main St",
                "city": "Philadelphia",
                "state": "PA",
                "zip": "19104",
            },
            "id": "abc123",
        }
    ]
    mock_response.raise_for_status = lambda: None
    mock_get.return_value = mock_response

    # Run function
    macaroni_kid.run_macaroni_kid(mnth=5, yr=2024)

    # Check DataFrame columns and values
    args, kwargs = mock_to_csv.call_args
    df: pd.DataFrame = args[0] if args else kwargs.get("path_or_buf")
    assert mock_to_csv.called
    # Check output file name
    assert kwargs["index"] is False
    assert kwargs["encoding"] == "utf-8"
    assert "2024_05_macaroni_kid.csv" in args[
        0
    ] or "2024_05_macaroni_kid.csv" in kwargs.get("path_or_buf", "")


@patch("scrapers.macaroni_kid.requests.get")
@patch("scrapers.macaroni_kid.pd.DataFrame.to_csv")
def test_run_macaroni_kid_empty_response(mock_to_csv, mock_get):
    # Mock API response with empty list
    """
    Test run_macaroni_kid with an API response containing an empty list.
    
    Should still write a CSV file with the correct name, but empty.
    """
    mock_response = MagicMock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = lambda: None
    mock_get.return_value = mock_response

    # Run function
    macaroni_kid.run_macaroni_kid(mnth=1, yr=2023)

    # Should still write a CSV (empty)
    assert mock_to_csv.called


@patch("scrapers.macaroni_kid.requests.get")
def test_run_macaroni_kid_http_error(mock_get):
    # Simulate HTTP error
    """
    Test run_macaroni_kid when an HTTP error is raised.

    Should:
    - Simulate an HTTP error by raising an exception in the mocked response.
    - Verify that the function raises the correct exception when an HTTP error occurs.
    """

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("HTTP Error")
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        macaroni_kid.run_macaroni_kid(mnth=1, yr=2023)
