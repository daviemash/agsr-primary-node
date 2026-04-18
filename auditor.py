import csv
import os
from datetime import datetime

LOG_FILE = "protocol_ledger.csv"

def initialize_ledger():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Agent_ID", "Action", "Fee_Accrued_ETH", "Status"])

def log_event(agent_id, action, fee, status):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, agent_id, action, fee, status])

initialize_ledger()