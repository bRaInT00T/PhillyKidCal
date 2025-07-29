"""
Fetch events from the Macaroni Kid API and saves them to a CSV file in the data folder
"""
import requests
import pandas as pd
from datetime import datetime
import json
from dateutil import parser
from urllib.parse import quote_plus

def run_macaroni_kid(mnth: int = None, yr: int = None):
    # Set your month and year
    now = datetime.now()
    if mnth is None: mnth = now.month
    if yr is None: yr = now.year
    if mnth < 10: mnth = f"0{mnth}"

    # Create ISO 8601 datetime strings
    start_date = f"{yr}-{mnth}-01T00:00:00.000Z"
    end_date = f"{yr}-{mnth}-31T23:59:59.000Z"

    # Construct the query JSON with dynamic dates
    query_dict = {
        "status": "active",
        "townOwner": "58252a826f1aaf645c94f61a",
        "startDate": start_date,
        "endDate": end_date,
    }

    # Convert to string manually to preserve JSON formatting
    query_json = json.dumps(query_dict)

    # Set API endpoint and params
    url = "https://api.macaronikid.com/api/v1/event/v2"
    params = {"query": query_json, "impression": "true"}


    # Fetch the data
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse the JSON response
    data = response.json()

    # Format the data into a list of dictionaries
    events = []
    for event in data:
        events.append(
            {
                "Title": event.get("title", ""),
                "Cost": event.get("cost", ""),
                "Start Date": event.get("startDateTime", ""),
                "End Date": event.get("endDateTime", ""),
                "Location": event.get("where", ""),
                "Tags": ", ".join([cat.get("name", "") for cat in event.get("categories", [])]),
                "Address": event["address"].get("street", "")
                + ", "
                + event["address"].get("city", "")
                + ", "
                + event["address"].get("state", "")
                + " "
                + event["address"].get("zip", ""),
                "Link": "https://downtownphilly.macaronikid.com/events/"
                + event.get("id", "")
                + "/"
                + quote_plus(event.get("title", "").replace(" ", "-")),
            }
        )

    for event in events:
        start_dt = parser.parse(event["Start Date"])
        end_dt = parser.parse(event["End Date"]) if event["End Date"] else None

        # Format date
        event["Date"] = start_dt.strftime("%Y-%m-%d")

        # Format time
        start_time = start_dt.strftime("%-I:%M %p")
        if end_dt and start_dt.date() == end_dt.date():
            end_time = end_dt.strftime("%-I:%M %p")
            event["Time"] = f"{start_time} - {end_time}"
        else:
            event["Time"] = start_time

        # Remove the original Start/End Date fields
        event.pop("Start Date")
        event.pop("End Date")

    # Create a DataFrame
    df = pd.DataFrame(events)
    df.rename(columns={"Cost": "Description"}, inplace=True)
    if not df.empty:
        df = df[["Date", "Time", "Title", "Location", "Description", "Tags", "Link"]]

    # print(df.head())
    outfile = f"data/{yr}_{mnth}_macaroni_kid.csv"
    df.to_csv(outfile, index=False, encoding='utf-8')
    print(f"\n✅ Wrote {len(df)} events to {outfile}")

if __name__ == "__main__":
    run_macaroni_kid()