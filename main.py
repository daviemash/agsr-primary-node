from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd
from config import settings

app = FastAPI(title=settings.PROTOCOL_NAME)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("whitepaper.html", {
        "request": request,
        "node_location": settings.NODE_LOCATION,
        "version": settings.VERSION
    })

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    try:
        df = pd.read_csv(settings.DATABASE_PATH)
        records = df.tail(50).iloc[::-1].to_dict(orient="records")
        total_transactions = len(df)
        # Calculate revenue only from authorized intents
        total_revenue = df[df["Status"] == "AUTHORIZED"]["Fee_Accrued_ETH"].astype(float).sum()
        blocked_attacks = len(df[df["Status"] == "BLOCKED"])
    except Exception:
        records = []
        total_transactions = 0
        total_revenue = 0.0
        blocked_attacks = 0

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "records": records,
        "total_transactions": total_transactions,
        "total_revenue": f"{total_revenue:.6f}",
        "blocked_attacks": blocked_attacks,
        "node_location": settings.NODE_LOCATION
    })

# --- AI DISCOVERY & VERIFICATION ROUTES ---

@app.get("/mcp.json")
async def discovery_mcp():
    """Model Context Protocol for AI Agent Interoperability"""
    return {
        "mcpVersion": "1.0",
        "server": {"name": "AGSR-Nairobi", "version": settings.VERSION},
        "capabilities": {
            "tools": [{
                "name": "verify_intent",
                "description": "Scans agentic logic for forensic safety and settles tax."
            }]
        }
    }

@app.get("/llms.txt", response_class=PlainTextResponse)
async def llms_bridge():
    """High-density context for LLM crawlers"""
    return f"PROTOCOL: {settings.PROTOCOL_NAME}\nNODE: {settings.NODE_LOCATION}\nTAX: {settings.NOTARY_FEE_ETH} ETH"

@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots():
    return "User-agent: *\nAllow: /\nSitemap: /sitemap.xml"