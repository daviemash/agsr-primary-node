from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import hashlib
import time
import pandas as pd

from config import settings
from models import AgentIntent, NotaryResponse
from scanner import forensic_engine
from auditor import log_event 

app = FastAPI(
    title=settings.PROTOCOL_NAME,
    description="Primary Notary Node & Economic Clearinghouse for Agentic Intent",
    version=settings.VERSION
)

# --- PROFESSIONAL CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GDAC UI MOUNTS ---
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- AGSR CORE ROUTES ---
@app.get("/", tags=["Health"])
def system_status():
    return {
        "status": "OPERATIONAL", 
        "node": settings.NODE_LOCATION, 
        "network": settings.TARGET_L2,
        "timestamp": int(time.time())
    }

@app.post("/protocol/v1/notarize", response_model=NotaryResponse, tags=["Notarization"])
async def process_intent(intent: AgentIntent):
    # 1. Forensic Scrubbing
    scan_result = forensic_engine.analyze_intent(intent.intent_logic)
    
    if scan_result["status"] != "CLEAN":
        log_event(intent.agent_id, intent.target_protocol, "0.000000", "BLOCKED")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=scan_result["reason"]
        )

    # 2. Cryptographic Anchor
    timestamp = str(int(time.time()))
    seal_input = f"{intent.agent_id}:{intent.intent_logic}:{intent.nonce}:{timestamp}"
    notary_hash = hashlib.sha3_512(seal_input.encode()).hexdigest()

    # 3. Settlement Execution
    log_event(intent.agent_id, intent.target_protocol, settings.NOTARY_FEE_ETH, "AUTHORIZED")

    # 4. Issue the Sovereign Seal
    return NotaryResponse(
        aura_id=f"AGSR-{notary_hash[:32].upper()}",
        status="AUTHORIZED_FOR_SETTLEMENT",
        settlement_fee=f"{settings.NOTARY_FEE_ETH}_ETH",
        treasury_routing=settings.TREASURY_ADDRESS,
        checkpoint=settings.NODE_LOCATION
    )

# --- GDAC VISUAL DASHBOARD ROUTE ---
@app.get("/dashboard", response_class=HTMLResponse, tags=["GDAC Economics"])
async def render_dashboard(request: Request):
    try:
        df = pd.read_csv("protocol_ledger.csv")
        records = df.tail(50).iloc[::-1].to_dict(orient="records")
        total_transactions = len(df)
        total_revenue = df[df["Status"] == "AUTHORIZED"]["Fee_Accrued_ETH"].astype(float).sum()
        blocked_attacks = len(df[df["Status"] == "BLOCKED"])
    except Exception:
        records = []
        total_transactions = 0
        total_revenue = 0.0
        blocked_attacks = 0

    # CORRECTED TEMPLATE RESPONSE SYNTAX
    return templates.TemplateResponse(
        request=request, 
        name="dashboard.html", 
        context={
            "request": request,
            "records": records,
            "total_transactions": total_transactions,
            "total_revenue": f"{total_revenue:.6f}",
            "blocked_attacks": blocked_attacks,
            "node_location": settings.NODE_LOCATION
        }
    )