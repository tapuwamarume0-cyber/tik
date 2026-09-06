from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime
from config import Config
from engine import TikTokEngine

app = FastAPI(title="Booster API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

campaigns = {}
logs = []

class CampaignRequest(BaseModel):
    targets: List[str]
    daily_limit: Optional[int] = Config.MAX_DAILY_ACTIONS

@app.get("/")
def root():
    return {"message": "booster api", "status": "online"}

@app.post("/campaign/start")
async def start_campaign(req: CampaignRequest, background_tasks: BackgroundTasks):
    campaign_id = str(uuid.uuid4())[:8]
    campaign = {
        "id": campaign_id,
        "status": "running",
        "targets": req.targets,
        "daily_limit": req.daily_limit,
        "created_at": datetime.utcnow().isoformat(),
        "results": []
    }
    campaigns[campaign_id] = campaign
    logs.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] campaign {campaign_id} started")
    
    background_tasks.add_task(run_campaign_task, campaign_id, req)
    return {"id": campaign_id, "status": "started"}

async def run_campaign_task(campaign_id: str, req: CampaignRequest):
    engine = TikTokEngine()
    results = await engine.run_campaign(req.targets)
    
    campaign = campaigns.get(campaign_id)
    if campaign:
        campaign["status"] = "completed"
        campaign["results"] = results
        logs.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] campaign {campaign_id} completed")

@app.get("/campaign/{campaign_id}")
def get_campaign(campaign_id: str):
    return campaigns.get(campaign_id, {"error": "not found"})

@app.get("/campaigns")
def list_campaigns():
    return list(campaigns.values())

@app.get("/logs")
def get_logs(limit: int = 20):
    return logs[-limit:]

@app.post("/campaign/{campaign_id}/stop")
def stop_campaign(campaign_id: str):
    campaign = campaigns.get(campaign_id)
    if campaign:
        campaign["status"] = "stopped"
        logs.append(f"[{datetime.utcnow().strftime('%H:%M:%S')}] campaign {campaign_id} stopped")
    return {"status": "stopped"}