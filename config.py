# config.py
import os

class Settings:
    PROTOCOL_NAME: str = "AGSR_Global_Sovereign_Registry"
    NODE_LOCATION: str = "Nairobi_Primary_01"
    VERSION: str = "1.0.0"
    
    # Economics
    TREASURY_ADDRESS: str = os.getenv("AGSR_TREASURY", "0xe69ae274c4d814fdb312120d3db1c5c2bd63a071")
    NOTARY_FEE_ETH: str = "0.000003"
    
    # Network
    TARGET_L2: str = "BASE_MAINNET"

settings = Settings()