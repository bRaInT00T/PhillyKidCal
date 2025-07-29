"""
Scrapes the Philly Family ical events and saves them to a CSV file
"""

import requests
from ics import Calendar
import pandas as pd
from datetime import datetime


def run_philly_fam(mnth: int = None, yr: int = None):
    # Get current month and year
    now = datetime.now()
    if mnth is None: mnth = now.strftime("%m")
    if yr is None: yr = now.strftime("%Y")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyPythonScript/1.0)"
    }

    url = "https://phillyfamily.com/events/?ical=1"
    response = requests.get(url, headers=headers)

    # Check content type and print if it's HTML (indicating an issue)
    if "text/calendar" not in response.headers.get("Content-Type", ""):
        print("Unexpected content type:", response.headers.get("Content-Type"))
        print("Response content:\n", response.text[:500])  # Print a preview for debug
        raise ValueError("Expected calendar data, but got something else")

    # Parse the calendar
    calendar = Calendar(response.text)

    # Parse events into a list of dictionaries
    events_data = []
    for event in calendar.events:
        start_date = event.begin.datetime if event.begin else None
        end_date = event.end.datetime if event.end else None

        if start_date and end_date:
            time_str = f"{start_date.strftime('%I:%M %p')} - {end_date.strftime('%I:%M %p')}"
        elif start_date:
            time_str = start_date.strftime('%I:%M %p')
        else:
            time_str = ""

        events_data.append(
            {
                "Date": start_date.date() if start_date else "",
                "Time": time_str,
                "Title": event.name,
                "Location": event.location,
                "Description": event.description.replace("\n\u00a0", " ") if event.description else "",
                "Tags": ", ".join(event.categories) if event.categories else "",
                "Link": str(event.url) if event.url else "",
            }
        )

    # Convert to a DataFrame
    df = pd.DataFrame(events_data)

    # Display the table
    # print(df.head())

    outfile = f"data/{yr}_{mnth}_philly_family.csv"    
    df.to_csv(outfile, index=False, encoding='utf-8')
    print(f"\n✅ Wrote {len(df)} events to {outfile}")


if __name__ == "__main__":
    run_philly_fam()