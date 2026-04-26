from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from config import settings

app = FastAPI(title=settings.PROTOCOL_NAME)
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
        df = pd.read_csv("protocol_ledger.csv")
        records = df.tail(50).iloc[::-1].to_dict(orient="records")
        total_transactions = len(df)
        total_revenue = df[df["Status"] == "AUTHORIZED"]["Fee_Accrued_ETH"].astype(float).sum()
        blocked_attacks = len(df[df["Status"] == "BLOCKED"])
    except Exception:
        records, total_transactions, total_revenue, blocked_attacks = [], 0, 0.0, 0

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "records": records,
        "total_transactions": total_transactions,
        "total_revenue": f"{total_revenue:.6f}",
        "blocked_attacks": blocked_attacks,
        "node_location": settings.NODE_LOCATION
    })

# AI Agent Handshake Route (AEO)
@app.get("/mcp.json")
async def mcp_discovery():
    return {"mcpVersion": "1.0", "capabilities": {"tools": [{"name": "tax_settlement"}]}}