from scrapers.macaroni_kid import run_macaroni_kid
from scrapers.mommy_poppins import run_mommy_poppins
from scrapers.philly_fam import run_philly_fam

from datetime import datetime
from glob import glob
import pandas as pd
import argparse


parser = argparse.ArgumentParser(description="Aggregate Philly kids events into a combined file.")
parser.add_argument("-m", "--month", type=int, help="Month (1-12) to scrape events for", default=datetime.now().month)
parser.add_argument("-y", "--year", type=int, help="Year to scrape events for", default=datetime.now().year)
parser.add_argument("--this-month", action="store_true", help="Use the current month and year")
parser.add_argument("--next-month", action="store_true", help="Use the next month and adjust year if needed")
args = parser.parse_args()

if args.next_month:
    if args.month != datetime.now().month:
        print("⚠️ '--next-month' overrides any --month/--year provided.")
    next_month_date = datetime(datetime.now().year, datetime.now().month, 1).replace(day=28) + pd.Timedelta(days=4)
    mnth = next_month_date.month
    yr = next_month_date.year
elif args.this_month:
    mnth = datetime.now().month
    yr = datetime.now().year
else:
    mnth = args.month
    yr = args.year

# Run scraping scripts
print(f"\rRunning run_macaroni_kid...", end='', flush=True)
run_macaroni_kid(mnth, yr)

print(f"\rRunning run_mommy_poppins...", end='', flush=True)
run_mommy_poppins(mnth, yr)

print(f"\rRunning run_philly_fam...", end='', flush=True)
run_philly_fam(mnth, yr)

# Load all CSVs from the data directory
csv_files = glob(f"./data/{yr}_{mnth}_*.csv")
print(f"Found CSV files: {csv_files}")

dataframes = []
for file in csv_files:
    df = pd.read_csv(file)
    dataframes.append(df)

# Combine all dataframes
combined_df = pd.concat(dataframes, ignore_index=True)

# Remove duplicates
combined_df = combined_df.drop_duplicates(subset=["Date", "Time", "Title", "Location"])

# Ensure Date and Time are strings and combine for sorting
combined_df["Date"] = combined_df["Date"].astype(str)
combined_df["Time"] = combined_df["Time"].fillna("")
combined_df["SortKey"] = combined_df["Date"] + " " + combined_df["Time"]

# Convert to datetime for sorting (handle missing time safely)
combined_df["SortKey"] = pd.to_datetime(combined_df["SortKey"], errors="coerce")

# Sort and drop helper column
combined_df = combined_df.sort_values(by="SortKey").drop(columns=["SortKey"])

# Output to combined CSV
mnth = f"{int(mnth):02d}" # Pad month with leading zero
outfile = f"./data/{yr}_{mnth}_kids_events.csv"
combined_df.to_csv(outfile, index=False, encoding='utf-8')
print(f"✅ Combined CSV created at {outfile}")

# Output to Excel file
excel_outfile = outfile.replace(".csv", ".xlsx")
combined_df.to_excel(excel_outfile, index=False, engine='openpyxl')
print(f"✅ Combined Excel file created at {excel_outfile}")
