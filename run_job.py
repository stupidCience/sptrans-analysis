# Arquivo: run_job.py (na raiz do projeto)
import time
import schedule
import os
from src.jobs.fetch_data_job import fetch_and_store_data

if not os.path.exists("data/temp_bus_data.db"):
    with open("data/temp_bus_data.db", "w"):
        pass


def start_scheduler():
    print("Starting the background scheduler... Fetching data every 2 minutes.")
    
    fetch_and_store_data()

    schedule.every(2).minutes.do(fetch_and_store_data)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")

if __name__ == "__main__":
    start_scheduler()