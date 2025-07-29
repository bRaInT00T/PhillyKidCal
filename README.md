# 🎡 PhillyKidCal

Combines family-friendly events from Philly-based calendars into one easy-to-use CSV and Excel schedule.

[![Python Version](https://img.shields.io/badge/python-3.13.1%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Last Update](https://img.shields.io/badge/last%20update-July%202025-orange)](#)

Scrapes family-friendly events in the Philadelphia area from **Macaroni Kid**, **Mommy Poppins**, and **Philly Family**. Outputs clean, deduplicated event lists in CSV and Excel formats.

---
This project aggregates family-friendly events in the Philadelphia area by scraping data from multiple sources and consolidating them into a single dataset in both CSV and Excel formats.

## 📚 Sources

- 🟣 [Macaroni Kid](https://macaronikid.com)
- 🟠 [Mommy Poppins](https://mommypoppins.com)
- 🔵 [Philly Family](https://phillyfamily.com)

## 🛠 Features

- ✅ Extracts event `Date`, `Time`, `Title`, `Location`, `Tags`, `Description`, and `Link`
- ✅ Combines results from all 3 sources
- ✅ Removes duplicate events
- ✅ Saves to both `.csv` and `.xlsx` in `data/` folder
- ✅ Easy to extend to other cities

## 🗂 Project Structure

```bash
kids_philly_events/
├── data/                          # Output files
│   ├── 2025_07_macaroni_kid.csv
│   ├── 2025_07_mommy_poppins.csv
│   ├── 2025_07_philly_family.csv
│   ├── 2025_07_kids_events.csv
│   └── 2025_07_kids_events.xlsx
├── macaroni_kid.py               # Fetch events from Macaroni Kid API
├── mommy_poppins.py              # Scrape events from Mommy Poppins
├── philly_fam.py                 # Parse iCalendar feed from Philly Family
├── main.py                       # Run all scrapers and join results
└── README.md                     # Project documentation
```

## ▶️ How to Run

```bash
pip install -r requirements.txt
python main.py
```

## 📝 Output Format

|Date|Time|Title|Location|Tags|Description|Link|
|-|-|-|-|-|-|-|
|2025-08-01|11:00 AM|Free Museum Day|Philly Museum|Family, Free|Enjoy free admission…|https://…|

## 🛠 Dependencies

- pandas
- requests
- ics
- beautifulsoup4
- openpyxl

## 📅 Scheduling (Optional)

You can schedule this to run daily/weekly using cron (Linux/macOS) or Task Scheduler (Windows).

Example cron job to run at 8am every Monday:

```bash
0 8 * * 1 /usr/bin/python3 /path/to/kids_philly_events/main.py
```

## 👤 Author

Nicholas Wolk
Philadelphia, PA
📧 [nwwolk@gmail.com](mailto:nwwolk@gmail.com)
📎 [LinkedIn](https://www.linkedin.com/in/nicholaswolk)

⸻

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.
