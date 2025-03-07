# backend/app.py
from fastapi import FastAPI, HTTPException
from tweepy import StreamingClient, OAuth2BearerHandler
from transformers import pipeline
from redis import Redis
from celery import Celery
import re
from geopy.distance import geodesic

app = FastAPI()
auth = OAuth2BearerHandler("YOUR_X_BEARER_TOKEN")  # Replace with real token
x_client = StreamingClient(auth)
classifier = pipeline("text-classification", model="distilbert-base-uncased")
redis_client = Redis(host="localhost", port=6379, db=0)
celery_app = Celery("grapevine", broker="redis://localhost:6379/0")

# Config (simplified for v1.0)
USER_CONFIG = {
    "zips": ["78701", "78702", "78703", ...],  # 20 zips (placeholder)
    "radius_center": None,  # e.g., (30.2672, -97.7431) for Austin
    "radius_miles": 25,
    "reps": [{"email": "owner@roofco.com", "phone": "+15125550123", "alerts": True},
             {"email": "rep1@roofco.com", "phone": "+15125550124", "alerts": True}],
    "extra_reps": 0  # Tracks >3 reps for billing
}

class LeadStreamer(StreamingClient):
    async def on_tweet(self, tweet):
        text = tweet.text.lower()
        result = classifier(text[:512])[0]
        if result["label"] == "POSITIVE" and result["score"] > 0.6:
            if result["score"] < 0.7 and not any(kw in text for kw in ["roof", "shingles", "house"]):
                return
            loc = self.get_location(tweet)
            if self.in_area(loc):
                lead = {"text": text, "loc": loc, "time": tweet.created_at, "score": result["score"]}
                await process_lead(lead)

    def get_location(self, tweet):
        if tweet.geo:
            return tweet.geo["coordinates"]
        zip_match = re.search(r"787\d{2}", tweet.text)
        return zip_match.group(0) if zip_match else "78701"  # Default Austin

    def in_area(self, loc):
        if isinstance(loc, str):  # Zip code
            return loc in USER_CONFIG["zips"]
        if USER_CONFIG["radius_center"]:  # Radius mode
            return geodesic(USER_CONFIG["radius_center"], loc).miles <= USER_CONFIG["radius_miles"]
        return False

async def process_lead(lead):
    zip_code = lead["loc"] if isinstance(lead["loc"], str) else "787xx"
    redis_client.zincrby("clusters", 1, zip_code)
    score = redis_client.zscore("clusters", zip_code)
    lead["priority"] = "high" if score >= 5 else "medium" if score >= 3 else "low"
    lead["cluster"] = f"{zip_code} - {int(score)} hits"
    if redis_client.llen("leads") < 50:  # Daily cap
        redis_client.lpush("leads", str(lead))
        celery_app.send_task("send_alerts", args=[lead])

@celery_app.task
def send_alerts(lead):
    from twilio.rest import Client
    twilio_client = Client("TWILIO_SID", "TWILIO_TOKEN")  # Replace with real creds
    for rep in USER_CONFIG["reps"]:
        if rep["alerts"]:
            twilio_client.messages.create(
                body=f"Lead: {lead['text'][:50]}... {lead['priority']}, {lead['cluster']}",
                from_="+12345678901",  # Replace with Twilio number
                to=rep["phone"]
            )
    # Email via SendGrid omitted for brevity—similar loop

streamer = LeadStreamer(auth)
streamer.add_rules(["wind damage 787xx -leak -flood"])  # Simplified for v1.0
streamer.filter(tweet_fields=["created_at", "geo"])

@app.get("/leads")
async def get_leads():
    leads = redis_client.lrange("leads", 0, 24)  # 25 leads/storm
    return [{"id": i, "data": eval(l.decode())} for i, l in enumerate(leads)]

@app.post("/settings")
async def update_settings(zips: list = None, radius: bool = False, reps: list = None):
    if zips and len(zips) <= 20:
        USER_CONFIG["zips"] = zips
        USER_CONFIG["radius_center"] = None
    elif radius:
        USER_CONFIG["radius_center"] = (30.2672, -97.7431)  # Austin default
        USER_CONFIG["zips"] = []
    if reps:
        USER_CONFIG["reps"] = reps[:3] if len(reps) <= 3 else reps
        USER_CONFIG["extra_reps"] = max(0, len(reps) - 3)
    return {"status": "Updated"}