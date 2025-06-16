from fastapi import FastAPI, Request
import json
import os

app = FastAPI()

SESSION_FILE = "session.json"

@app.post("/webhook/review")
async def handle_review_webhook(request: Request):
    data = await request.json()
    with open(SESSION_FILE, "w") as f:
        json.dump(data, f)
    return {"status": "received"}

@app.post("/webhook/status")
async def handle_status_webhook(request: Request):
    data = await request.json()
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_data = json.load(f)
        session_data["status"] = data.get("status", session_data.get("status", ""))
        with open(SESSION_FILE, "w") as f:
            json.dump(session_data, f)
    return {"status": "received"}
