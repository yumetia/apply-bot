# ⚠️ Important: Update Before Running

Before using this tool, make sure to update the following values in the `email_sender.py` file:

- Your personal email address (`EMAIL`)
- Your Gmail App Password (`APP_PASSWORD`)
- The path to your resume file (`CV_PATH`)

If these are not set correctly, the program will fail to send emails.

---

# 📬 ApplyBot — Automatic Email Scraper & Sender for Internship Applications

This project automates the process of discovering new companies, scraping their contact information (email, phone, city), and sending personalized internship application emails with your CV attached.

---

## ⚙️ Features

- 🔍 Scrapes companies using DuckDuckGo (keywords + domain extraction)
- 📬 Extracts email, phone number, and city (via website parsing)
- 📄 Logs all contacts in a `suivi.csv` file with status tracking
- 📧 Sends emails with a CV PDF attached
- 🧠 Avoids duplicates and skips companies already contacted

---

## 🧰 Requirements

- Python 3.8+
- A Gmail account with [App Passwords](https://support.google.com/accounts/answer/185833) enabled
- Internet connection

---

## 🗂️ Project Structure

apply-bot/
│
├── main.py # Triggers email sending
├── pipeline.py # Finds new companies and enriches contact data
├── email_sender.py # Sends emails based on CSV data
├── web_scraper.py # Scrapes websites and contact info
├── utils.py # CSV read/write helpers
├── suivi.csv # Your application history (auto-managed)
└── README.md # This file

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yumetia/apply-bot.git
cd apply-bot
```

### 2. Configure your personal settings

Open email_sender.py and update these lines:

EMAIL        = "your_email@gmail.com"
APP_PASSWORD = "your_gmail_app_password"
CV_PATH      = "your_resume.pdf"

### 3. Prepare your CV

Place your PDF resume (e.g., your_resume.pdf) in the project root folder.

### 4. Run the pipeline to find companies

```bash 
python pipeline.py
```
This script will:

    Search DuckDuckGo using pre-defined keywords

    Extract company domains

    Try to scrape email, phone number, and city

    Add new entries to suivi.csv with status en attente

### 5. Send your emails

```bash 
python main.py
```
This script will:

    Send emails only to companies that:

        Have status en attente

        Have not yet been contacted today

    Update their status to Envoyé

    Record the date in the Relance column

### 📝 Example CSV (suivi.csv)

Entreprise;Email;Status;Date de postulat;Relance;Lieu;Mindset;Numero
DevWebCo;contact@devwebco.fr;en attente;04/07/2025;;Paris;;0123456789

### Tips

    Edit or add your own keywords in pipeline.py → KEYWORDS list

    Don't run the script too frequently to avoid being rate-limited

    To retry sending emails, manually update Status and Relance in suivi.csv

### 📌 License

This project is open source and free to use.

Let me know if you'd like this file saved, translated, or zipped with your code as a GitHub-ready package.

See ya !