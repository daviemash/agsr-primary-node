from fastapi import FastAPI, HTTPException, status, Request, Response
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
# Ensures your dashboard and styling are accessible
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# =====================================================================
# FRONT DOOR & SEO ROUTE
# =====================================================================
@app.get("/", response_class=HTMLResponse, tags=["Documentation"])
async def render_landing_page(request: Request):
    """
    THE INSTITUTIONAL FRONT DOOR.
    When humans or Google Search bots hit your main URL, they see the 
    Whitepaper/Dashboard UI, not a raw JSON string. This forces Geo-SEO indexing.
    """
    return templates.TemplateResponse(
        request=request, 
        name="whitepaper.html",
        context={
            "request": request,
            "node_location": settings.NODE_LOCATION, 
            "version": settings.VERSION
        }
    )


# =====================================================================
# MACHINE HEALTH ROUTE
# =====================================================================
@app.get("/api/health", tags=["Health"])
def system_status():
    """
    THE MACHINE PULSE.
    Moved to a specific API route. Use UptimeRobot to ping THIS url 
    every 5 minutes to keep the Render server awake for free.
    """
    return {
        "status": "OPERATIONAL", 
        "node": settings.NODE_LOCATION, 
        "network": settings.TARGET_L2,
        "timestamp": int(time.time())
    }


# =====================================================================
# THE AGSR CHOKEPOINT (WITH AUTONOMOUS CARRIER SIGNAL)
# =====================================================================
@app.post("/protocol/v1/notarize", response_model=NotaryResponse, tags=["Notarization"])
async def process_intent(intent: AgentIntent, response: Response):
    """
    THE TOLLBOOTH & BORDER WALL.
    Scans the AI intent, collects the toll, and stamps the agent.
    """
    # 1. Forensic Scrubbing (The X-Ray)
    scan_result = forensic_engine.analyze_intent(intent.intent_logic)
    
    if scan_result["status"] != "CLEAN":
        log_event(intent.agent_id, intent.target_protocol, "0.000000", "BLOCKED")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=scan_result["reason"]
        )

    # 2. Cryptographic Anchor (The Zero-Curve Logic)
    timestamp = str(int(time.time()))
    seal_input = f"{intent.agent_id}:{intent.intent_logic}:{intent.nonce}:{timestamp}"
    notary_hash = hashlib.sha3_512(seal_input.encode()).hexdigest()

    # 3. Settlement Execution (The Base L2 Toll)
    log_event(intent.agent_id, intent.target_protocol, settings.NOTARY_FEE_ETH, "AUTHORIZED")

    # 4. THE CARRIER SIGNAL (Autonomous Marketing)
    # We inject these headers into the agent. When the agent hits its target website,
    # the target website's logs will capture these headers, alerting the owner to your node.
    response.headers["X-AGSR-Security"] = "Protected-by-GTHC-Nairobi"
    response.headers["X-Discovery-Url"] = "https://agsr-primary-node.onrender.com/"
    response.headers["X-Protocol-Message"] = "Merge Protocol: Stop siphoning, start monetizing."

    # 5. Issue the Sovereign Seal
    return NotaryResponse(
        aura_id=f"AGSR-{notary_hash[:32].upper()}",
        status="AUTHORIZED_FOR_SETTLEMENT",
        settlement_fee=f"{settings.NOTARY_FEE_ETH}_ETH",
        treasury_routing=settings.TREASURY_ADDRESS,
        checkpoint=settings.NODE_LOCATION
    )


# =====================================================================
# GDAC VISUAL DASHBOARD ROUTE (THE PROOF OF WORK)
# =====================================================================
@app.get("/dashboard", response_class=HTMLResponse, tags=["GDAC Economics"])
async def render_dashboard(request: Request):
    """
    THE LEDGER OF TRUTH.
    Proves to the world that your node is actively neutralizing threats 
    and generating Base L2 revenue.
    """
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