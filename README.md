# ✈️ Flight Radar: Automated Batch Flight Scraper & Analytics Dashboard

> **Bringing Order to Chaos: Pure, Transparent Flight Comparison**

A Streamlit-powered flight price aggregator and data analysis tool designed to eliminate manual, day-by-day flight searches across dynamic single-page applications (SPAs).

---

## 💡 Motivation & Philosophy

Planning a trip often comes with two major frustrations:
1. **Information Overload**: Booking platforms are heavily cluttered with ads, complex transit options, and distracting pop-ups.
2. **Tedious Day-by-Day Searching**: Traditional sites force users to manually query dates one by one, wait for repeated page reloads, and hand-record fluctuating fares.

**Flight Radar** transforms chaotic flight data into structured, transparent, and actionable insights. Simply define your desired travel window, and the crawler automatically queries, extracts, and compiles all available flights in batch.

---

## 🚀 Key Features

* 📅 **Batch Date-Range Scraping**: Query an entire travel window in a single run without repetitive manual clicks.
* 🎯 **Curated Top Recommendations**: Automatically filters and highlights the most cost-effective and optimal flights.
* 🧳 **True Baggage-Inclusive Pricing**: Simulates real browser actions to select baggage options dynamically, capturing genuine total costs rather than misleading base fares.
* 🗄️ **Structured SQLite Persistence**: Stores airlines, departure/arrival times, durations, currencies, and luggage policies for instantaneous historical retrieval and comparison.
* 🔍 **Interactive Multi-Filter Dashboard**: Filter flights by route, airline, baggage status, currency, and date with real-time table controls.

---

## 🛠️ Tech Stack & Architecture

* **UI & Dashboard**: [Streamlit](https://streamlit.io/)
* **Browser Automation**: `undetected-chromedriver`, `Selenium` (bypasses anti-bot barriers and interacts with dynamic React UI states)
* **Semantic Parsing**: `BeautifulSoup4`, `Regex` (targets robust `data-testid` and `data-code` attributes)
* **Data Processing**: `pandas`
* **Local Storage**: `SQLite3` (utilizes batch transactions for efficient deduplication)

---

## 📦 Getting Started

### Prerequisites
* Python 3.9+
* Google Chrome installed on your machine

### 1. Clone the Repository
```bash
git clone [https://github.com/](https://github.com/)<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2. Create and Activate a Virtual Environment

* **macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

* **Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install streamlit selenium undetected-chromedriver beautifulsoup4 pandas
```

### 4. Run the Application
```bash
streamlit run app.py
```

---

## 📂 Project Structure

```text
├── app.py                 # Main Streamlit dashboard & UI logic
├── scraper.py             # Selenium & undetected-chromedriver crawler logic
├── database.py            # SQLite database schema, inserts, and queries
├── airlines.db            # Local SQLite database (generated automatically)
└── README.md              # Project documentation
```

---

## ⚠️ Limitations & Roadmap

### Current Limitations

* **Rendering Latency**: Due to real-time Online Travel Agency (OTA) backend queries, each daily search requires a 6–8 second rendering buffer.
* **Single Platform Scope**: Optimized primarily for Trip.com; multi-OTA aggregation is not yet supported.
* **Anti-Scraping Thresholds**: High-frequency concurrent queries across long date ranges may trigger interactive CAPTCHA challenges.

### Planned Roadmap

* [ ] **Expanded City & Multi-Currency Support**: Add global airport codes and live currency conversion (e.g., JPY, MYR, USD, TWD).
* [ ] **Historical Price Trend Visualizations**: Add integrated interactive charts tracking price trends across dates.
* [ ] **Headless Cloud Deployment**: Containerize with Docker for scheduled background crawls.

---

## ⚖️ Disclaimer

This project is intended strictly for educational and personal research purposes. Respect the Terms of Service (ToS) and rate limits of the targeted travel platforms.
