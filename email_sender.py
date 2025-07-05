import smtplib
import re
import csv
import datetime
from email.message import EmailMessage
from web_scraper import extract_email_phone_city_from_site

# === CONFIGURATION ===
EMAIL = "your_email@gmail.com"           # ← Replace with your email
APP_PASSWORD = "your_app_password"       # ← Replace with your Gmail App password
CV_PATH = "YOUR_CV.pdf"                  # ← Replace with your actual CV filename
CSV_FILE = "suivi.csv"
EMAIL_SUBJECT = "Spontaneous Application – Fullstack Web Developer (Apprenticeship)"

EMAIL_RE = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")

# change this template to your custom one
EMAIL_BODY = """
Hello,

I'm currently a student looking for a web development apprenticeship starting in September 2025. I'm passionate about web technologies and eager to apply my skills in a professional environment.

Through my education and self-driven projects, I have gained solid experience in frontend (React, TailwindCSS) and backend (Node.js, Python, Laravel, Symfony) development, as well as agile teamwork.

Attached is my resume. Thank you for your time and consideration.

Best regards,
YOUR NAME
📞 YOUR PHONE
📧 your_email@gmail.com
🌐 your-portfolio.com
"""

# --- Email sender function ---
def send_email(recipient: str) -> bool:
    try:
        msg = EmailMessage()
        msg["Subject"] = EMAIL_SUBJECT
        msg["From"] = EMAIL
        msg["To"] = recipient
        msg.set_content(EMAIL_BODY)

        with open(CV_PATH, "rb") as cv:
            msg.add_attachment(cv.read(), maintype="application", subtype="pdf", filename=CV_PATH)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL, APP_PASSWORD)
            smtp.send_message(msg)
        return True

    except Exception as e:
        print(f"[ERROR] {recipient} → {e.__class__.__name__}")
        return False


# --- Main logic for processing and updating the CSV ---
def process_and_update_csv() -> None:
    today = datetime.datetime.now().strftime("%d/%m/%Y")
    updated_rows = []

    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    for row in rows:
        status = row.get("Status", "").strip().lower()
        post_date = row.get("Date de postulat", "").strip()
        relances = row.get("Relance", "")
        email_orig = row.get("Email", "").strip()
        email_to_send = None

        # Skip rows that are not marked "en attente"
        if status != "en attente":
            updated_rows.append(row)
            continue

        # Skip rows already contacted today
        if today in relances:
            updated_rows.append(row)
            continue

        # --- Determine if scraping is needed ---
        if post_date == today:
            # Newly added rows: try to scrape email if not valid
            if EMAIL_RE.match(email_orig):
                email_to_send = email_orig
            else:
                scraped_email, _, _ = extract_email_phone_city_from_site(row["Entreprise"])
                if scraped_email and EMAIL_RE.match(scraped_email):
                    email_to_send = scraped_email
                    row["Email"] = scraped_email
                    print(f"[SCRAPED] {row['Entreprise']} → {scraped_email}")
                else:
                    print(f"[SKIP] No usable email found for (new) {row['Entreprise']}")
        else:
            # Older rows: only use original email if valid
            if EMAIL_RE.match(email_orig):
                email_to_send = email_orig
                print(f"[SEND OLD] {row['Entreprise']} → {email_orig}")
            else:
                print(f"[SKIP] Invalid email for (old) {row['Entreprise']}")

        if not email_to_send:
            updated_rows.append(row)
            continue

        # --- Send email ---
        if send_email(email_to_send):
            row["Status"] = "Envoyé"
            row["Relance"] = f"{relances}, {today}".strip(", ")
            print(f"[OK] Email sent to {row['Entreprise']}")
        else:
            print(f"[FAIL] Failed to send email to {row['Entreprise']}")

        updated_rows.append(row)

    # --- Write updated CSV back ---
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(updated_rows)


if __name__ == "__main__":
    process_and_update_csv()
