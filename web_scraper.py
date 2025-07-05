import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

# --- Regex Patterns ---
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}")

# --- Perform DuckDuckGo HTML search ---
def ddg_search(query: str, max_results: int = 5) -> list[str]:
    url = "https://html.duckduckgo.com/html/"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.post(url, data={"q": query}, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        return [a["href"] for a in soup.select("a.result__a") if a.get("href")][:max_results]
    except Exception:
        return []

# --- Extract all matching emails from text ---
def extract_emails(text: str) -> list[str]:
    return EMAIL_REGEX.findall(text)

# --- Extract all matching French-format phone numbers from text ---
def extract_phones(text: str) -> list[str]:
    return PHONE_REGEX.findall(text)

# --- Fetch HTML page and parse for emails, phones, and body text ---
def scrape_page(url: str) -> tuple[list[str], list[str], str]:
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=6, allow_redirects=True)
        if resp.status_code >= 400:
            return [], [], ""
        html = resp.text
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(" ", strip=True)

        # Extract from "mailto:" links
        mailtos = [
            a["href"].split("mailto:")[1].split("?")[0]
            for a in soup.select("a[href^='mailto:']")
            if "mailto:" in a["href"]
        ]
        emails = list(dict.fromkeys(mailtos + extract_emails(html)))
        phones = extract_phones(text)

        return emails, phones, text.lower()
    except Exception:
        return [], [], ""

# --- Main function to extract email, phone, and city ---
def extract_email_phone_city_from_site(company_name: str) -> tuple[str | None, str | None, str | None]:
    """
    Return (email, phone, city) tuple, or (None, None, None) if nothing is found.
    """
    search_keywords = [
        f"{company_name} official site",
        f"{company_name} contact",
        f"{company_name} email"
    ]

    candidates: list[str] = []
    for keyword in search_keywords:
        candidates += ddg_search(keyword, max_results=5)

    # Common contact page paths
    contact_paths = [
        "/", "/contact", "/contact-us", "/contacts", "/contactez-nous",
        "/nous-contacter", "/mentions-legales", "/legal"
    ]

    urls_to_scrape: list[str] = []
    visited_domains: set[str] = set()

    for url in candidates:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path
        if not domain or domain in visited_domains:
            continue
        visited_domains.add(domain)
        base_url = f"https://{domain}"
        for path in contact_paths:
            urls_to_scrape.append(urljoin(base_url, path))

    known_cities = [
        "marseille","aix-en-provence"
    ]

    for page_url in urls_to_scrape:
        emails, phones, text = scrape_page(page_url)
        if not emails and not phones and not text:
            continue

        # Prioritize common business email prefixes
        priority_emails = [e for e in emails if re.search(r"(contact|info|admin|hello)", e, re.I)]
        selected_email = priority_emails[0] if priority_emails else (emails[0] if emails else None)
        selected_phone = phones[0] if phones else None
        city_found = next((c.title() for c in known_cities if c in text), None)

        if selected_email or selected_phone or city_found:
            return selected_email, selected_phone, city_found

    return None, None, None
