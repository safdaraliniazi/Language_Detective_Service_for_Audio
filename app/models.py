from pydantic import BaseModel
from typing import Optional, List, Dict

class DetectionRequest(BaseModel):
    audio_file_path: str
    ground_truth_language: Optional[str] = None

class ProviderResult(BaseModel):
    provider: str
    detected_language: Optional[str] = None
    time_taken: float
    estimated_cost: Dict[str, float]
    status: str
    error_message: Optional[str] = None

class DetectionResponse(BaseModel):
    results: List[ProviderResult]
