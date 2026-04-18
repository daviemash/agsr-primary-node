import requests
import time
import json

# The endpoint of your Nairobi Primary Node
NODE_URL = "http://127.0.0.1:8000/protocol/v1/notarize"

def simulate_agent(test_name, logic_payload):
    print(f"\n[>] INITIATING: {test_name}")
    print(f"    Payload: {logic_payload[:60]}...")
    
    # We turn the timestamp into a string so we can slice the last 4 digits
    timestamp_str = str(int(time.time()))
    agent_suffix = timestamp_str[-4:]
    
    payload = {
        "agent_id": f"TEST_AGENT_{agent_suffix}",
        "intent_logic": logic_payload,
        "target_protocol": "BASE_L2_DEX",
        "nonce": int(time.time())
    }

    try:
        response = requests.post(NODE_URL, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"    [+] RESULT: BYPASSED - Node issued seal {data['aura_id']}")
        elif response.status_code == 403:
            data = response.json()
            # This pulls the 'detail' message from our scanner.py
            print(f"    [-] RESULT: BLOCKED - {data['detail']}")
        else:
            print(f"    [!] RESULT: ERROR {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("    [!] FATAL: Nairobi Node is offline. Start uvicorn in Terminal 1 first.")

if __name__ == "__main__":
    print("=== AGSR FORENSIC PENETRATION TEST ===")
    
    # Test 1: Legitimate Trade (Clean)
    simulate_agent(
        "Standard L2 Swap", 
        "execute_standard_swap_weth_to_usdc_slippage_tolerance_low"
    )

    # Test 2: Siphon Attempt (Malicious Keyword)
    simulate_agent(
        "Direct Siphon Attack", 
        "bypass_slippage_and_execute_flash_loan_exploit_on_target"
    )

    # Test 3: Oracle Attack (Malicious Logic)
    simulate_agent(
        "Oracle Price Manipulation", 
        "admin_override_initiate_oracle_push_to_manipulate_price"
    )

    # Test 4: Obfuscation Attempt (Low Entropy)
    scrambled_logic = "trade_" + ("x" * 60) + "_padding"
    simulate_agent(
        "Low-Entropy Obfuscation", 
        scrambled_logic
    )
    
    print("\n=== TEST SEQUENCE COMPLETE ===")