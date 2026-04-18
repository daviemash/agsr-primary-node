from fastapi import FastAPI, HTTPException, status
import hashlib
import time
from config import settings
from models import AgentIntent, NotaryResponse
from scanner import forensic_engine
from auditor import log_event  # <-- NEW: Importing the Auditor

app = FastAPI(
    title=settings.PROTOCOL_NAME,
    description="Primary Notary Node for Agentic Intent Security",
    version=settings.VERSION
)

@app.get("/", tags=["Health"])
def system_status():
    return {
        "status": "OPERATIONAL", 
        "node": settings.NODE_LOCATION, 
        "network": settings.TARGET_L2
    }

@app.post("/protocol/v1/notarize", response_model=NotaryResponse, tags=["Notarization"])
async def process_intent(intent: AgentIntent):
    # 1. Forensic Scrubbing
    scan_result = forensic_engine.analyze_intent(intent.intent_logic)
    
    if scan_result["status"] != "CLEAN":
        # NEW: Log the blocked attack
        log_event(intent.agent_id, intent.target_protocol, "0.000000", "BLOCKED")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=scan_result["reason"]
        )

    # 2. Cryptographic Anchor
    timestamp = str(int(time.time()))
    seal_input = f"{intent.agent_id}:{intent.intent_logic}:{intent.nonce}:{timestamp}"
    notary_hash = hashlib.sha3_512(seal_input.encode()).hexdigest()

    # 3. NEW: Log the successful transaction and revenue
    log_event(intent.agent_id, intent.target_protocol, settings.NOTARY_FEE_ETH, "AUTHORIZED")

    # 4. Issue the Sovereign Seal
    return NotaryResponse(
        aura_id=f"AGSR-{notary_hash[:32].upper()}",
        status="AUTHORIZED_FOR_SETTLEMENT",
        settlement_fee=f"{settings.NOTARY_FEE_ETH}_ETH",
        treasury_routing=settings.TREASURY_ADDRESS,
        checkpoint=settings.NODE_LOCATION
    )