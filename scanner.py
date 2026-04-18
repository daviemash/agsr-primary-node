# scanner.py
import re

class AgsrImmuneSystem:
    def __init__(self):
        # The ever-evolving database of agentic exploits
        self.malicious_regex = [
            r"(price_manipulation|oracle_push|set_price)", 
            r"(drain|withdraw_all|emergency_exit|siphon)",        
            r"(self_destruct|delegate_call|flash_loan_exploit)"               
        ]

    def analyze_intent(self, raw_intent: str) -> dict:
        intent_lower = raw_intent.lower()
        
        # 1. Advanced Regex Threat Detection
        for pattern in self.malicious_regex:
            if re.search(pattern, intent_lower):
                return {
                    "status": "REJECTED", 
                    "reason": f"ADVERSARIAL_LOGIC_DETECTED: Threat Signature [{pattern}]"
                }
        
        # 2. Minimum Entropy & Complexity Threshold
        unique_chars = len(set(intent_lower))
        if len(intent_lower) > 50 and (unique_chars / len(intent_lower)) < 0.2:
            return {
                "status": "REJECTED", 
                "reason": "SUSPICIOUS_ENTROPY: Payload appears artificially obfuscated."
            }

        return {"status": "CLEAN", "reason": "Forensic analysis passed."}

forensic_engine = AgsrImmuneSystem()