import re
from typing import Dict, Any

class ForensicEngine:
    def __init__(self):
        # Compiling regex patterns at startup saves memory and CPU time
        self.siphon_patterns = re.compile(r"(self_destruct|delegate_call|flash_loan_exploit|drain_liquidity)", re.IGNORECASE)
        self.oracle_patterns = re.compile(r"(price_manipulation|oracle_push|set_price|override_feed)", re.IGNORECASE)
        
    def analyze_intent(self, payload: str) -> Dict[str, Any]:
        """Scans the agent's payload against known adversarial threat signatures."""
        
        # 1. Check for Siphoning / Drain Attacks
        if self.siphon_patterns.search(payload):
            return {"status": "THREAT", "reason": "ADVERSARIAL_LOGIC_DETECTED: Threat Signature [Siphon/Drain]"}
            
        # 2. Check for Oracle / Data Manipulation
        if self.oracle_patterns.search(payload):
            return {"status": "THREAT", "reason": "ADVERSARIAL_LOGIC_DETECTED: Threat Signature [Oracle Manipulation]"}
            
        # 3. Check for Obfuscation (Payloads that look artificially hidden)
        if payload.count('x') > 20 or len(payload) > 1000:
            return {"status": "THREAT", "reason": "SUSPICIOUS_ENTROPY: Payload appears artificially obfuscated."}
            
        return {"status": "CLEAN", "reason": "No threats detected."}

# Instantiate a single global engine to save memory
forensic_engine = ForensicEngine()