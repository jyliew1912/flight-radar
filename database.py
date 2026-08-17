import sqlite3

DB_NAME = "airlines.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 建立包含 departure_city 與 arrival_city 的資料表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            airline TEXT,
            departure_time TEXT,
            arrival_time TEXT,
            flight_duration TEXT,
            is_direct TEXT,
            has_baggage TEXT,
            unit_price TEXT,
            total_price TEXT,
            quantity INTEGER,
            departure_city TEXT,
            arrival_city TEXT,
            currency TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_post(data_list, departure_city="", arrival_city="", currency=""):
    """支援接收單一字典 (dict) 或航班列表 (list)，並寫入出發與抵達城市"""
    if not data_list:
        return
    
    init_db()  # 確保資料表已建立

    if isinstance(data_list, dict):
        data_list = [data_list]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        records = [
            (
                item.get('date', ''),
                item.get('airline', ''),
                item.get('departure_time', ''),
                item.get('arrival_time', ''),
                item.get('flight_duration', ''),
                item.get('is_direct', ''),
                item.get('has_baggage', ''),
                item.get('unit_price', ''),
                item.get('total_price', ''),
                item.get('quantity', 0),
                item.get('departure_city', departure_city), 
                item.get('arrival_city', arrival_city),
                item.get('currency', currency)
            )
            for item in data_list
        ]
        
        cursor.executemany('''
            INSERT INTO posts (
                date, airline, departure_time, arrival_time, flight_duration, 
                is_direct, has_baggage, unit_price, total_price, quantity, 
                departure_city, arrival_city, currency
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', records)
        
        conn.commit()
        print(f"💾 Successfully inserted {len(records)} flight records into SQLite database!")
    except Exception as e:
        print(f"❌ Failed to insert into database: {e}")
    finally:
        conn.close()