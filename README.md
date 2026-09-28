# ✈️ Flight Radar: Automated Batch Flight Scraper & Analytics Dashboard

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python)](https://www.python.org/)
[![UI: Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg?logo=streamlit)](https://streamlit.io/)
[![Engine: Selenium](https://img.shields.io/badge/Engine-Selenium%20%7C%20Undetected--Chromedriver-brightgreen.svg)](https://github.com/ultrafunkamsterdam/undetected-chromedriver)
[![Database: SQLite3](https://img.shields.io/badge/Storage-SQLite3-blue.svg?logo=sqlite)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An automated web intelligence tool and interactive analytics dashboard designed to eliminate manual, day-by-day flight searches across dynamic Single-Page Applications (SPAs).

Built with **Python**, **Selenium (`undetected-chromedriver`)**, **BeautifulSoup4**, and **Streamlit**, Flight Radar extracts authentic, baggage-inclusive airfares across multi-day travel windows and structures them into an interactive local query engine.

## 📽️ Interactive Demonstration

[![Flight Radar Demo](https://img.youtube.com/vi/YlMGw_ylDjo/maxresdefault.jpg)](https://youtu.be/YlMGw_ylDjo)

> 📹 **[Click here to watch the full demo on YouTube](https://youtu.be/YlMGw_ylDjo)**  
> *Walkthrough demonstrating multi-date batch crawling, dynamic React UI interaction, and real-time SQLite filtering.*

*Demonstrating multi-date automated batch scraping, dynamic React filter interactions, and instant SQLite query filtering.*

## 💡 Motivation & Philosophy

Planning a trip often comes with two major frustrations:
1. **Information Overload:** Booking platforms are heavily cluttered with ads, complex transit options, and distracting pop-ups.
2. **Tedious Day-by-Day Searching:** Traditional sites force users to manually query dates one by one, wait for repeated page reloads, and hand-record fluctuating fares across multiple days.

**Flight Radar** transforms chaotic flight data into structured, transparent, and actionable insights. Simply define your desired travel window, and the crawler automatically queries, extracts, and compiles all available flights in batch.


## 🚀 Key Features

* 📅 **Batch Date-Range Scraping:** Query an entire travel window (1–10 consecutive days) in a single automated run without repetitive manual clicks.
* 🎯 **Curated Top Recommendations:** Automatically filters and highlights the most cost-effective and optimal flights per departure date.
* 🧳 **True Baggage-Inclusive Pricing:** Simulates browser actions to select checked-baggage options dynamically, capturing genuine total costs rather than misleading base fares.
* 🗄️ **Structured SQLite Persistence:** Stores airlines, departure/arrival times, durations, currencies, and luggage policies for instantaneous historical retrieval and comparison.
* 🔍 **Interactive Multi-Filter Dashboard:** Filter flights by route, airline, direct/transit hops, baggage status, currency, and date with real-time table controls and row-hiding capabilities.


## 🛠️ Tech Stack & Architecture

* **UI & Dashboard:** Streamlit
* **Browser Automation:** `undetected-chromedriver`, Selenium (bypasses anti-bot barriers and interacts with dynamic React UI states)
* **Semantic Parsing:** BeautifulSoup4, Regex (targets robust `data-testid` and `data-code` attributes)
* **Data Processing:** pandas
* **Local Storage:** SQLite3 (utilizes batch transactions for efficient deduplication and fast queries)


## 📂 Project Structure

```text
flight-radar/
├── app.py                 # Main Streamlit dashboard & reactive UI logic
├── scraper.py             # Selenium & undetected-chromedriver crawler logic
├── database.py            # SQLite database schema, inserts, and queries
├── requirements.txt       # Pegged Python dependencies
├── airlines.db            # Local SQLite database (generated automatically upon crawl)
└── README.md              # Project documentation
```

## 📦 Getting Started

### Prerequisites

* **Python 3.9+**
* **Google Chrome** installed on your machine

### 1. Clone the Repository

```bash
git clone https://github.com/jyliew1912/flight-radar.git
cd flight-radar
```

### 2. Set Up Virtual Environment & Dependencies

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux / macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

```bash
streamlit run app.py
```

> **Note on Chrome & WebDriver:**
> `undetected-chromedriver` manages browser binaries automatically. If an automated driver mismatch occurs after a Chrome update, specify your browser's major version inside `scraper.py` (e.g., `version_main=153`) or clear the cached driver folder in `%APPDATA%\undetected_chromedriver`.


## ⚠️ Limitations & Roadmap

### Current Limitations

* **Rendering Latency:** Due to real-time Online Travel Agency (OTA) backend queries, each daily search requires a 6–8 second rendering buffer to prevent anti-bot throttling.
* **Single Platform Scope:** Optimized primarily for Trip.com; multi-OTA aggregation is not yet supported.
* **Anti-Scraping Thresholds:** High-frequency concurrent queries across long date ranges may trigger interactive CAPTCHA challenges.

### Planned Roadmap

* [ ] **Expanded City & Multi-Currency Support:** Add global airport codes and live currency conversion (e.g., JPY, MYR, USD, TWD).
* [ ] **Historical Price Trend Visualizations:** Add integrated interactive charts tracking price trends across dates.
* [ ] **Headless Cloud Deployment:** Containerize with Docker for scheduled background crawls.


## ⚖️ Disclaimer

This project is intended strictly for educational and personal research purposes. Users must respect the Terms of Service (ToS) and rate limits of the targeted travel platforms.
