from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from .models import TriageRequest, TriageResponse
from .agent import analyze_finance_message
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Finance Triage Agent API",
    description="Automates triage and response drafting for finance communications."
)

# Setup CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/triage", response_model=TriageResponse)
async def triage_endpoint(request: TriageRequest):
    return analyze_finance_message(request)

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Finance Triage Agent API"}
    
# Serve the frontend UI exactly on port 8000 too!
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
