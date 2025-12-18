# python heartbeat.py
import time
from datetime import datetime

while True:
    print(f"[{datetime.now()}] Container alive...")
    time.sleep(5)
