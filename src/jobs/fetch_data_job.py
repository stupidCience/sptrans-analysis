import os
import sqlite3
import polars as pl
from datetime import datetime, timedelta
from src.middlewares.api_client import SPTransAPIClient

def fetch_and_store_data():
    print("Starting background job to update bus positions...")
    api_client = SPTransAPIClient()

    try:
        data = api_client.get_bus_positions()
    except Exception as e:
        print(f"Job failed: {e}")
        return

    bus_list = []

    if 'l' in data:
        for line in data['l']:
            direction = "Outbound" if line.get('sl') == 1 else "Inbound" if line.get('sl') == 2 else "Unknown"
            destination = line.get('lt0', 'Unknown')
            origin = line.get('lt1', 'Unknown')

            for bus in line['vs']:
                raw_time = bus.get('ta', '')
                try:
                    clean_time = raw_time[:-1] if raw_time.endswith('Z') else raw_time
                    dt_utc = datetime.fromisoformat(clean_time)
                    dt_local = dt_utc - timedelta(hours=3)
                    update_date = dt_local.strftime("%d/%m/%Y")
                    update_time = dt_local.strftime("%H:%M:%S")
                except Exception:
                    update_date = "Unknown"
                    update_time = raw_time

                bus_list.append({
                    'line_id': line['c'],
                    'origin': origin,
                    'destination': destination,
                    'direction': direction,
                    'bus_prefix': str(bus['p']),
                    'latitude': float(bus['py']),
                    'longitude': float(bus['px']),
                    'update_date': update_date,
                    'update_time': update_time,
                    'is_accessible': bool(bus['a']),
                    'captured_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Carimbo do Histórico
                })

    if bus_list:
        df = pl.DataFrame(bus_list)
        df_clean = df.drop_nulls(subset=["latitude", "longitude"])

        db_path = "data/temp_bus_data.db"
        conn = sqlite3.connect(db_path, timeout=20)
        conn.execute("PRAGMA journal_mode=WAL;")
        
        conn.execute("CREATE TABLE IF NOT EXISTS bus_positions ("
                     "line_id TEXT, origin TEXT, destination TEXT, direction TEXT, "
                     "bus_prefix TEXT, latitude REAL, longitude REAL, "
                     "update_date TEXT, update_time TEXT, is_accessible BOOLEAN, "
                     "captured_at TEXT)")

        conn.executemany(
            "INSERT INTO bus_positions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            df_clean.rows()
        )

        # Apaga apenas os dados muito velhos (mais de 6 horas)
        conn.execute("DELETE FROM bus_positions WHERE captured_at <= datetime('now', '-6 hours')")

        conn.commit()
        conn.close()
        print(f"Successfully added {len(df_clean)} positions. History rolling window maintained.")
    else:
        print("No bus data found in the current request.")

if __name__ == "__main__":
    fetch_and_store_data()
