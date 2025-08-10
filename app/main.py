from fastapi import FastAPI
from app.models import DetectionRequest, DetectionResponse
from app.coordinator.orchestrator import orchestrate_language_detection
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="DripLink Language Detector")

@app.post("/detect/language", response_model=DetectionResponse)
async def detect_language(request: DetectionRequest):
    results = await orchestrate_language_detection(request.audio_file_path)
    return DetectionResponse(results=results)
