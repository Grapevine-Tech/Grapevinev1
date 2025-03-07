from fastapi import FastAPI, HTTPException
import os
from redis import Redis
import asyncio

app = FastAPI()

# Redis setup (uses REDIS_URL from Render)
redis_client = Redis.from_url(os.getenv("REDIS_URL"))

# Dummy leads for testing
DUMMY_LEADS = [
    {"id": 1, "data": {"text": "Wind hit 78702", "loc": [30.2672, -97.7431], "cluster": "78702 - 5 hits", "priority": "high"}},
    {"id": 2, "data": {"text": "Hail in 78704", "loc": [30.245, -97.755], "cluster": "78704 - 3 hits", "priority": "medium"}},
    {"id": 3, "data": {"text": "Roof damage 78701", "loc": [30.271, -97.741], "cluster": "78701 - 2 hits", "priority": "low"}}
]

@app.get("/leads")
async def get_leads():
    # Simulate storing leads in Redis
    if not redis_client.exists("leads"):
        for lead in DUMMY_LEADS:
            redis_client.lpush("leads", str(lead))
    leads = redis_client.lrange("leads", 0, 24)  # Limit to 25 leads
    return [{"id": i, "data": eval(l.decode())} for i, l in enumerate(leads)]

@app.post("/settings")
async def update_settings(zips: list = None, radius: bool = False, reps: list = None):
    # Placeholder for future settings logic
    return {"status": "Settings updated (dummy response)"}