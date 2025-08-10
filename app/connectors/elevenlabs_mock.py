import time
from app.models import ProviderResult

async def detect_language_openai_mock(audio_file_path: str) -> ProviderResult:
    start_time = time.time()
    return ProviderResult(
        provider="OpenAI (Mock)",
        detected_language="en",
        time_taken=time.time() - start_time,
        estimated_cost={"tokens": 0, "dollars": 0},
        status="success"
    )

async def detect_language_elevenlabs_mock(audio_file_path: str) -> ProviderResult:
    start_time = time.time()
    return ProviderResult(
        provider="ElevenLabs (Mock)",
        detected_language="en",
        time_taken=time.time() - start_time,
        estimated_cost={"tokens": 0, "dollars": 0},
        status="success"
    )
