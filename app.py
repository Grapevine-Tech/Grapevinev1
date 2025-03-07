from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (adjust for prod later)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# In-memory dummy leads
DUMMY_LEADS = [
    {"id": 1, "data": {"text": "Wind hit 78702", "loc": [30.2672, -97.7431], "cluster": "78702 - 5 hits", "priority": "high"}},
    {"id": 2, "data": {"text": "Hail in 78704", "loc": [30.245, -97.755], "cluster": "78704 - 3 hits", "priority": "medium"}},
    {"id": 3, "data": {"text": "Roof damage 78701", "loc": [30.271, -97.741], "cluster": "78701 - 2 hits", "priority": "low"}}
]

@app.get("/leads")
async def get_leads():
    return DUMMY_LEADS

@app.post("/settings")
async def update_settings(zips: list = None, radius: bool = False, reps: list = None):
    return {"status": "Settings updated (dummy response)"}
