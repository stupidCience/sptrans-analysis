import sqlite3
import polars as pl

class BusModel:
    def __init__(self):
        self.db_path = "data/temp_bus_data.db"

    def _read_table(self):
        try:
            conn = sqlite3.connect(self.db_path, timeout=20)
            conn.execute("PRAGMA journal_mode=WAL;")
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM bus_positions")
            rows = cursor.fetchall()
            
            if not rows:
                return pl.DataFrame()

            columns = [description[0] for description in cursor.description]
            
            return pl.DataFrame(rows, schema=columns, orient="row")
            
        except sqlite3.OperationalError as e:
            print(f"Database error: {e}")
            return pl.DataFrame()
        finally:
            if 'conn' in locals():
                conn.close()

    def get_current_positions(self):
        df = self._read_table()
        if not df.is_empty():
            df = df.sort("captured_at").group_by("bus_prefix").last()
        return df

    def get_historical_positions(self):
        return self._read_table()