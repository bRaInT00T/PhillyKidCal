"""
Scrapes events from mommypoppins.com by parsing HTML.
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def run_mommy_poppins(mnth: int = None, yr: int = None):
    now = datetime.now()
    if mnth is None: mnth = now.month
    if yr is None: yr = now.year
    if mnth < 10: mnth = f"0{mnth}"

    url = "https://mommypoppins.com/events/1146/philadelphia/all/tag/all/age/all/all/all/type/deals/0/near/0/0"
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(resp.text, "html.parser")

    def extract_max_page(soup):
        pager = soup.select_one("div.pager-wrapper")
        if not pager:
            return 1
        return max(
            int(a.get_text(strip=True))
            for a in pager.select("a")
            if a.get_text(strip=True).isdigit()
        )

    max_page = extract_max_page(soup)

    base_url = "https://mommypoppins.com/events/1146/philadelphia/all/tag/all/age/all/all/all/type/deals/0/near/0/{}"

    events = []

    for page in range(max_page):
        page_url = base_url.format(page)
        print(f"\rFetching: {page + 1} of {max_page} ({((page + 1) / max_page) * 100:.0f}%)", end='', flush=True)
        resp = requests.get(page_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")

        container = soup.select_one("div.list-container")
        if not container:
            print(f"❌ Could not find .list-container on page {page}")
            continue

        for block in container.find_all(recursive=False):
            date_elem = block.select_one(".events-date-header")
            if date_elem:
                raw_date = date_elem.get_text(strip=True)
                try:
                    parsed_date = datetime.strptime(raw_date, "%a, %b %d")
                    current_date = parsed_date.replace(year=yr).strftime("%Y-%m-%d")
                except ValueError:
                    current_date = raw_date  # fallback
            else:
                current_date = "Unknown Date"

            for event in block.select(".list-item.event"):
                card = event.select_one("div.content-details")
                if not card:
                    continue

                title = card.select_one("h2")
                location = card.select_one("div[style] > span")
                description = card.select_one("noscript")

                tag_elements = card.select("div.specialtags span.tag")
                tags = [tag.get_text(strip=True) for tag in tag_elements]

                time_elem = event.select_one(".times-label")
                time = time_elem.get_text(strip=True).replace("All dates and times", "").strip() if time_elem else "N/A"

                events.append({
                    "Date": current_date,
                    "Time": time,
                    "Title": title.get_text(strip=True) if title else "N/A",
                    "Location": location.get_text(strip=True) if location else "N/A",
                    "Description": description.get_text(strip=True) if description else "N/A",
                    "Tags": ", ".join(tags),
                    "Link": "https://mommypoppins.com" + event.select_one("a").get("href")
                })

    df = pd.DataFrame(events)
    # print(df.head())
    outfile = f"data/{yr}_{mnth}_mommy_poppins.csv"
    df.to_csv(outfile, index=False, encoding='utf-8')
    print(f"\n✅ Wrote {len(df)} events to {outfile}")

if __name__ == "__main__":
    run_mommy_poppins()