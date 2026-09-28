import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import sqlite3
from scraper import main
import os

st.set_page_config(
    page_title="Multi-Date Flight Fare Tracker",
    page_icon="✈️",
    layout="wide"
)

# ----------------------------------------------------
# City List Mapping
# ----------------------------------------------------
# Check whether is matched with Trip.com
CITIES = {
    "台北桃園 (TPE)": "tpe",
    "高雄機場 (KHH)": "khh",
    "大阪關西 (KIX)": "osa",
    "檳城 (PEN)": "pen",
    "吉隆坡 (KUL)": "kul",
    "新加坡 (SIN)": "sin",
    "曼谷素萬那普 (BKK)": "bkk",
    "香港 (HKG)": "hkg"
}

# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
with st.sidebar:
    st.markdown("# 🧭 Page Navigation")
    current_page = st.radio(
        "Go To Page...",
        ["✈️ Flight Search", "⛁ History Database", "ℹ️ About"],
        index=0
    )
    st.markdown("---")
    st.caption("Trip.com Crawler Engine v2.0")

# ----------------------------------------------------
# MAIN PAGE
# ----------------------------------------------------
if current_page == "✈️ Flight Search":
    col_logo, col_title = st.columns([1, 4], vertical_alignment="center")
    with col_logo:
        st.image("my_logo.jpg", width=300)
    with col_title:
        st.title("Multi-Date Flight Fare Tracker")
        st.caption("Search the lowest prices flight across multiple dates on Trip.com")

    st.markdown("---")

    with st.container():
        st.subheader("🔍 Flight Search Settings")
        st.caption(
            ":yellow[This tool allows you to search only one-way flights between two cities on Trip.com, across multiple consecutive days.]"
            "\n\n"
            ":green[The results will be stored in a local SQLite database for later analysis.]"
        )
        
        row1_col1, row1_col2, row1_col3 = st.columns(3)
        with row1_col1:
            dep_display = st.selectbox("Departure City", options=list(CITIES.keys())) 
            departure_city = CITIES[dep_display]
        with row1_col2:
            arr_display = st.selectbox("Arrival City", options=list(CITIES.keys()), index=2) 
            arrival_city = CITIES[arr_display]
        with row1_col3:
            currency = st.selectbox("Currency", ["TWD","MYR"], index=0)

        row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
        with row2_col1:
            default_search_date = datetime.today() + timedelta(days=7)
            start_date = st.date_input("Departure Date Search", value=default_search_date)
        with row2_col2:
            days_to_scrape = st.number_input("Search Consecutive Days", min_value=1, max_value=10, value=5)
        with row2_col3:
            quantity = st.number_input("Passenger Count", min_value=1, max_value=5, value=1)
        with row2_col4:
            top_n = st.number_input("Daily Top N Flights", min_value=1, max_value=5, value=4)

        need_baggage = st.checkbox("Show flights with checked baggage only", value=False)
        
        search_submitted = st.button("🚀 Start Search", type="primary", use_container_width=True)

    if search_submitted:
        st.info("Starting the flight search process. Please wait...")
        main(
            start_date=start_date.strftime("%Y-%m-%d"),
            days_to_scrape=days_to_scrape,
            departure_city=departure_city,
            arrival_city=arrival_city,
            currency=currency,
            quantity=quantity,
            top_n=top_n,
            need_baggage=need_baggage
        )
        st.success("Flight search completed! Check the database for results.")

# ----------------------------------------------------
# DATABASE PAGE
# ----------------------------------------------------
elif current_page == "⛁ History Database":
    st.title("⛁ History Database")
    st.caption("View, filter, and customize flight records stored in the database.")
    st.markdown("---")
    
    if 'hidden_flight_ids' not in st.session_state:
        st.session_state['hidden_flight_ids'] = set()

    try:
        conn = sqlite3.connect('airlines.db')
        df_db = pd.read_sql_query("SELECT * FROM posts ORDER BY created_at DESC", conn)
        conn.close()

        if df_db.empty:
            st.info("💡 The database currently has no flight records. Please go to the '✈️ Flight Search' page to scrape data.")
        else:
            df_db['price_num'] = pd.to_numeric(
                df_db['unit_price'].astype(str).str.replace(',', '', regex=False).str.extract(r'(\d+)', expand=False),
                errors='coerce'
            )

            # ================= 1. Filter Panel =================
            with st.expander("🔍 Click to expand/collapse the data filter panel (Filter Panel)", expanded=True):
                f_col1, f_col2, f_col3 = st.columns(3)
                with f_col1:
                    dep_city_options = ["All"] + sorted(df_db['departure_city'].dropna().unique().tolist()) if 'departure_city' in df_db.columns else ["All"]
                    selected_dep_city = st.selectbox("Departure City", dep_city_options)
                    
                with f_col2:
                    arr_city_options = ["All"] + sorted(df_db['arrival_city'].dropna().unique().tolist()) if 'arrival_city' in df_db.columns else ["All"]
                    selected_arr_city = st.selectbox("Arrival City", arr_city_options)
                    
                with f_col3:
                    airline_options = ["All"] + sorted(df_db['airline'].dropna().unique().tolist()) if 'airline' in df_db.columns else ["All"]
                    selected_airline = st.selectbox("Airline", airline_options)

                f_col4, f_col5, f_col6 = st.columns(3)
                with f_col4:
                    direct_options = ["All", "Direct", "Transit"]
                    selected_direct = st.selectbox("Flight Type", direct_options)
                    
                with f_col5:
                    baggage_options = ["All", "With Baggage", "No Baggage"]
                    selected_baggage = st.selectbox("Checked Baggage", baggage_options)

                with f_col6:
                    currency_options = sorted(df_db['currency'].dropna().unique().tolist()) if 'currency' in df_db.columns else ["All"]
                    selected_currency = st.selectbox("Currency", currency_options)

                f_col7, f_col8 = st.columns(2)
                with f_col7:
                    available_dates = sorted(df_db['date'].dropna().unique().tolist()) if 'date' in df_db.columns else []
                    selected_dates = st.multiselect("Departure Date", available_dates, default=available_dates)
                    
                with f_col8:
                    sort_option = st.selectbox("Sort By", [
                        "Created At (Newest First)",
                        "Unit Price (Low to High)",
                        "Unit Price (High to Low)",
                        "Departure Date (Near to Far)"
                    ])

            # ================= 2. Apply Filters =================
            filtered_df = df_db.copy()

            if st.session_state['hidden_flight_ids'] and 'id' in filtered_df.columns:
                filtered_df = filtered_df[~filtered_df['id'].isin(st.session_state['hidden_flight_ids'])]

            if 'departure_city' in filtered_df.columns and selected_dep_city != "All":
                filtered_df = filtered_df[filtered_df['departure_city'] == selected_dep_city]

            if 'arrival_city' in filtered_df.columns and selected_arr_city != "All":
                filtered_df = filtered_df[filtered_df['arrival_city'] == selected_arr_city]

            if selected_airline != "All":
                filtered_df = filtered_df[filtered_df['airline'] == selected_airline]

            if selected_direct == "Direct":
                filtered_df = filtered_df[filtered_df['is_direct'].astype(str).str.contains("直飛")]
            elif selected_direct == "Transit":
                filtered_df = filtered_df[~filtered_df['is_direct'].astype(str).str.contains("直飛")]

            if selected_baggage == "With Baggage":
                filtered_df = filtered_df[filtered_df['has_baggage'].astype(str).str.contains("託運|Checked", case=False, na=False)]
            elif selected_baggage == "No Baggage":
                filtered_df = filtered_df[~filtered_df['has_baggage'].astype(str).str.contains("託運|Checked", case=False, na=False)]

            if selected_currency:
                filtered_df = filtered_df[filtered_df['currency'].astype(str).str.contains(selected_currency)]

            if selected_dates:
                filtered_df = filtered_df[filtered_df['date'].isin(selected_dates)]

            if sort_option == "Unit Price (Low to High)":
                filtered_df = filtered_df.sort_values(by="price_num", ascending=True)
            elif sort_option == "Unit Price (High to Low)":
                filtered_df = filtered_df.sort_values(by="price_num", ascending=False)
            elif sort_option == "Departure Date (Near to Far)":
                filtered_df = filtered_df.sort_values(by="date", ascending=True)
            else:
                filtered_df = filtered_df.sort_values(by="created_at", ascending=False)

            filtered_df = filtered_df.reset_index(drop=True)

            # ================= 3. Statistics =================
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Visible Records", f"{len(filtered_df)} records")
            
            if not filtered_df.empty and filtered_df['price_num'].notnull().any():
                min_price = int(filtered_df['price_num'].min())
                avg_price = int(filtered_df['price_num'].mean())
                m2.metric("Current Lowest Price", f"TWD {min_price:,}")
                m3.metric("Current Average Price", f"TWD {avg_price:,}")
            else:
                m2.metric("Current Lowest Price", "N/A")
                m3.metric("Current Average Price", "N/A")

            m4.metric("Hidden Records", f"{len(st.session_state['hidden_flight_ids'])} hidden")

            cols_to_drop = [c for c in ['price_num'] if c in filtered_df.columns]
            display_df = filtered_df.drop(columns=cols_to_drop)

            # ================= 4. Table Display with Row Selection =================
            st.caption("💡 *Tip: You can select/check rows in the table below and click 'Hide Selected' to filter out unwanted times.*")

            # Unshow some of the column
            cols_to_show = [c for c in display_df.columns if c not in ['id', 'currency']]

            # 🎯 multi-row selection
            event = st.dataframe(
                display_df, 
                column_order=cols_to_show, 
                use_container_width=True, 
                hide_index=True,
                on_select="rerun",
                selection_mode="multi-row"
            )

            # ================= 5. Hide & Restore Action Buttons =================
            selected_rows = event.selection.rows if hasattr(event, 'selection') else []
            
            btn_col1, btn_col2, btn_spacer = st.columns([2, 2, 4])
            
            with btn_col1:
                if st.button(f"👁️ Hide Selected ({len(selected_rows)}) Rows", disabled=(len(selected_rows) == 0), use_container_width=True):
                    selected_ids = filtered_df.iloc[selected_rows]['id'].tolist()
                    st.session_state['hidden_flight_ids'].update(selected_ids)
                    st.toast(f"✅ Hidden {len(selected_ids)} flight records.")
                    st.rerun()

            with btn_col2:
                if st.button(f"🔄 Restore All ({len(st.session_state['hidden_flight_ids'])}) Hidden", disabled=(len(st.session_state['hidden_flight_ids']) == 0), use_container_width=True):
                    st.session_state['hidden_flight_ids'] = set()
                    st.toast("✅ Restored all hidden flight records.")
                    st.rerun()

            # ================= 6. Export (Left) & Delete (Far Right) =================
            st.markdown("---")
            col_left, col_spacer, col_right = st.columns([3, 4, 2])

            with col_left:
                csv_data = display_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Export Filtered Results (CSV / Excel)",
                    data=csv_data,
                    file_name=f"flights_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            with col_right:
                with st.popover("🗑️ Reset Database Records", use_container_width=True):
                    st.warning("⚠️ This will permanently clear all recorded flight history.")
                    if st.button("Confirm Table Truncation", type="primary", use_container_width=True):
                        try:
                            with sqlite3.connect('airlines.db') as conn:
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM posts;")
                                conn.commit()
                            st.session_state['hidden_flight_ids'] = set()
                            st.toast("✅ Flight records cleared successfully.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to reset records: {e}")

    except Exception as e:
        st.error(f"Failed to read from database: {e}")

# ----------------------------------------------------
# ABOUT PAGE
# ----------------------------------------------------
elif current_page == "ℹ️ About":
    st.title("ℹ️ About This Project")
    st.markdown("---")
    st.markdown("""
    ### 💡 Motivation & Philosophy
    > **Bringing Order to Chaos: Pure, Transparent Flight Comparison**

    Planning a trip often comes with two major frustrations:
    1. **Information Overload**: Booking sites are crowded with ads, pop-ups, and overwhelming connection options.
    2. **Tedious Day-by-Day Searching**: Traditional platforms make it painful to compare flights across a flexible date range. Travelers are forced to manually click through each day one by one, wait for pages to reload, and keep track of fluctuating prices and flight schedules by hand. **With this tool, you simply define a date range, and the system automatically scrapes and compiles all available flights in batch—effortlessly and efficiently.**

    Driven by a passion for **data organization and decluttering**, this project was built to transform chaotic, dynamically rendered flight pages into structured, transparent, and actionable data.

    ---

    ### 🚀 Key Features
    * **Batch Date-Range Scraping**: Define your travel window once, and let the crawler aggregate daily flights automatically.
    * **Curated Top Recommendations**: Extracts only the best-value flights, saving you from scrolling through dozens of irrelevant options.
    * **True Baggage-Inclusive Pricing**: Automated browser interactions tick the "Checked Baggage" filter dynamically, fetching realistic total prices rather than misleading budget fares.
    * **Structured & Persistent Data**: Parses airlines, departure/arrival times, durations, baggage allowance, and total costs into clean SQLite records for seamless analysis.

    ---

    ### 🛠️ Architecture & Tech Stack
    * **Dynamic Parameter Assembly**: Converts user queries (origin, destination, travel dates, passenger count) into standardized URL parameters.
    * **Browser Automation (`undetected-chromedriver` + `Selenium`)**: Bypasses anti-bot barriers on Single Page Applications (SPAs) and triggers complex React UI filter states using `ActionChains`.
    * **Semantic Parsing (`BeautifulSoup` + Regex)**: Targets resilient `data-testid` and `data-code` attributes instead of volatile randomized CSS classes.
    * **Lightweight Storage (`SQLite3`)**: Manages records with batch transactions (`executemany`) for efficient deduplication and data retrieval.

    ---

    ### ⚠️ Limitations & Future Roadmap

    **Current Limitations:**
    * **Rendering Latency**: Because Online Travel Agencies (OTAs) query airline reservation systems in real time, each daily search requires a 6–8 second rendering buffer.
    * **Single Platform Scope**: Currently optimized for Trip.com; does not yet aggregate across multiple platforms simultaneously (e.g., Skyscanner, Google Flights).
    * **Anti-Scraping Thresholds**: High-frequency concurrent searches across long date ranges may occasionally trigger interactive CAPTCHA verification.

    **Roadmap:**
    * [ ] **Expanded City & Currency Coverage**: Support a wider selection of global airports, city pairs, and multi-currency conversions (e.g., JPY, MYR).
    * [ ] **Price Trend Visualizations**: Interactive historical price tracking and date-range comparison charts built directly into the dashboard.
    """)
