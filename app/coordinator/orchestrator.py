import asyncio
from typing import List
from app.models import ProviderResult
from app.connectors.google_gemini import detect_language_google_gemini
from app.connectors.sarvam_ai import detect_language_sarvam
from app.connectors.openai_mock import detect_language_openai_mock
from app.connectors.elevenlabs_mock import detect_language_elevenlabs_mock

async def orchestrate_language_detection(audio_file_path: str) -> List[ProviderResult]:
    tasks = [
        detect_language_google_gemini(audio_file_path),
        detect_language_sarvam(audio_file_path),
        detect_language_openai_mock(audio_file_path),
        detect_language_elevenlabs_mock(audio_file_path)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    final_results = []
    for result, connector_name in zip(results, ["Google Gemini", "Sarvam AI", "OpenAI Mock", "ElevenLabs Mock"]):
        if isinstance(result, Exception):
            final_results.append(ProviderResult(
                provider=connector_name,
                detected_language=None,
                time_taken=0,
                estimated_cost={"tokens": 0, "dollars": 0},
                status="error",
                error_message=str(result)
            ))
        else:
            final_results.append(result)

    return final_results
