import csv
import os
import logging
from datetime import datetime

# Configure professional cloud logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("AGSR_Auditor")

LEDGER_FILE = "protocol_ledger.csv"

def initialize_ledger():
    """Creates the ledger with strict headers if it does not exist."""
    if not os.path.exists(LEDGER_FILE):
        try:
            with open(LEDGER_FILE, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Agent_ID", "Action", "Fee_Accrued_ETH", "Status"])
            logger.info("Genesis block of protocol_ledger.csv created successfully.")
        except IOError as e:
            logger.error(f"CRITICAL ERROR: Could not create ledger. {e}")

def log_event(agent_id: str, action: str, fee: str, status: str):
    """Appends an event to the ledger safely."""
    initialize_ledger()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    try:
        with open(LEDGER_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, agent_id, action, fee, status])
        
        # Log to the Render Cloud Console
        if status == "BLOCKED":
            logger.warning(f"THREAT BLOCKED | Agent: {agent_id} | Action: {action}")
        else:
            logger.info(f"AUTHORIZED | Agent: {agent_id} | Fee: {fee}")
            
    except IOError as e:
        logger.error(f"FILE LOCK ERROR: Dropped log for {agent_id}. Error: {e}")

# Run initialization on boot
initialize_ledger()