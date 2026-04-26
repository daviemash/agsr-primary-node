from fastapi import FastAPI, HTTPException, status, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
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

# =====================================================================
# FRONT DOOR ROUTE
# =====================================================================
@app.get("/", response_class=HTMLResponse, tags=["Documentation"])
async def render_landing_page(request: Request):
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
# SEO & DISCOVERY ROUTES (THE MAP)
# =====================================================================
@app.get("/robots.txt", response_class=PlainTextResponse, tags=["Discovery"])
def robots_txt():
    return """User-agent: *
Allow: /
Allow: /dashboard
Allow: /whitepaper
Allow: /mcp.json

Sitemap: https://agsr-primary-node.onrender.com/sitemap.xml
"""

@app.get("/sitemap.xml", tags=["Discovery"])
def sitemap_xml():
    sitemap = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://agsr-primary-node.onrender.com/</loc>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://agsr-primary-node.onrender.com/dashboard</loc>
    <changefreq>hourly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>"""
    return Response(content=sitemap, media_type="application/xml")

# =====================================================================
# MACHINE HEALTH & AEO ROUTE
# =====================================================================
@app.get("/api/health", tags=["Health"])
def system_status():
    return {
        "status": "OPERATIONAL",
        "node": settings.NODE_LOCATION,
        "network": settings.TARGET_L2,
        "timestamp": int(time.time())
    }

@app.get("/mcp.json", tags=["Discovery"])
async def serve_mcp_protocol():
    """Broadcasts the Model Context Protocol to Advanced AI Agents"""
    return FileResponse("mcp.json", media_type="application/json")

# =====================================================================
# THE AGSR CHOKEPOINT
# =====================================================================
@app.post("/protocol/v1/notarize", response_model=NotaryResponse, tags=["Notarization"])
async def process_intent(intent: AgentIntent, response: Response):
    scan_result = forensic_engine.analyze_intent(intent.intent_logic)
 
    if scan_result["status"] != "CLEAN":
        log_event(intent.agent_id, intent.target_protocol, "0.000000", "BLOCKED")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=scan_result["reason"]
        )

    timestamp = str(int(time.time()))
    seal_input = f"{intent.agent_id}:{intent.intent_logic}:{intent.nonce}:{timestamp}"
    notary_hash = hashlib.sha3_512(seal_input.encode()).hexdigest()

    log_event(intent.agent_id, intent.target_protocol, settings.NOTARY_FEE_ETH, "AUTHORIZED")

    response.headers["X-AGSR-Security"] = "Protected-by-AGSR-Nairobi"
    response.headers["X-Discovery-Url"] = "https://agsr-primary-node.onrender.com/"
    response.headers["X-Protocol-Message"] = "GDAC Merge Available: Stop siphoning, start monetizing."

    return NotaryResponse(
        aura_id=f"AGSR-{notary_hash[:32].upper()}",
        status="AUTHORIZED_FOR_SETTLEMENT",
        settlement_fee=f"{settings.NOTARY_FEE_ETH}_ETH",
        treasury_routing=settings.TREASURY_ADDRESS,
        checkpoint=settings.NODE_LOCATION
    )

# =====================================================================
# GDAC VISUAL DASHBOARD ROUTE
# =====================================================================
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