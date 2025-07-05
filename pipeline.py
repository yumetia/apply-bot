
# 1. Perform DuckDuckGo(google is not working properly I dont know why) search based on location & sector keywords
# 2. Scrape emails, phone numbers, and location
# 3. Add to CSV with status='pending'
# 4. Save the enriched data

import sys, time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

from utils import lire_csv, enregistrer_csv
from web_scraper import ddg_search, extract_email_phone_city_from_site

CSV_FILE = Path('suivi.csv')

KEYWORDS = [
    # Major zones
    "agence web marseille", "startup marseille",
    "agence web aix en provence", "startup aix en provence",
    # add more according to your mobility !
]

# --- Step 1: Detect new companies not already in CSV ---
def find_new_companies(existing_rows: List[Dict[str, str]]) -> List[str]:
    known_names = {row['Entreprise'].lower() for row in existing_rows if row.get('Entreprise')}
    new_candidates = set()
    for keyword in KEYWORDS:
        urls = ddg_search(keyword, max_results=10)
        for url in urls:
            domain = url.split('//')[-1].split('/')[0]
            parts = domain.split('.')
            if len(parts) >= 2:
                company_name = parts[-2].capitalize()
                if company_name.lower() not in known_names:
                    new_candidates.add(company_name)
        time.sleep(2)
    return list(new_candidates)

# --- Step 2: Enrich data and save into CSV ---
def pipeline():
    if not CSV_FILE.exists():
        print('suivi.csv not found')
        sys.exit(1)

    existing_rows = lire_csv(CSV_FILE)
    new_names = find_new_companies(existing_rows)

    if not new_names:
        print('No new companies found.')
        return

    today = datetime.today().strftime('%d/%m/%Y')
    print(f'🔎 Found new company names: {new_names}')

    for name in new_names:
        email, phone, city = extract_email_phone_city_from_site(name)

        # Skip if no valid email found
        if not email or '@' not in email:
            print(f"[SKIP] No usable email for {name}")
            continue

        existing_rows.append({
            'Entreprise':       name,
            'Email':            email or '',
            'Status':           'en attente',
            'Date de postulat': today,
            'Relance':          '',
            'Lieu':             city or '',
            'Mindset':          '',
            'Numero':           phone or ''
        })

    enregistrer_csv(CSV_FILE, existing_rows)
    print(f'CSV updated with {len(new_names)} new companies.')
    print('Pipeline complete. You can now run email_sender file.ex: python email_sender.py')

if __name__ == '__main__':
    pipeline()
