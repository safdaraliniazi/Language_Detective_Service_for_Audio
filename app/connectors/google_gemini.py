import os
import time
from app.models import ProviderResult
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import asyncio
from asyncio import to_thread
from app.utils.pricing import calculate_cost

# MIME types
MIME_TYPES = {
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/x-m4a",
    ".flac": "audio/flac",
    # etc etc
}
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

async def detect_language_google_gemini(audio_file_path: str) -> ProviderResult:
    """
    Detects the language of an audio file using the Google Gemini 1.5 Flash model.

    This function dynamically determines the audio's MIME type based on its file extension,
    making it compatible with various audio formats.

    Args:
        audio_file_path (str): The path to the audio file.

    Returns:
        ProviderResult: An object containing the detection result,
                        time taken, and estimated cost.
    """
    start_time = time.time()
    # --- 1. Initial Validation ---
    if not GOOGLE_API_KEY:
        return ProviderResult(
            provider="Google Gemini",
            detected_language=None,
            time_taken=0,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="error",
            error_message="GOOGLE_API_KEY environment variable is not set."
        )

    audio_bytes = None

    # Determine the MIME type
    file_extension = os.path.splitext(audio_file_path)[1].lower()
    mime_type = MIME_TYPES.get(file_extension)

    if not mime_type:
        # Return an error if the file extension is not supported
        return ProviderResult(
            provider="Google Gemini",
            detected_language=None,
            time_taken=time.time() - start_time,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="error",
            error_message=f"Unsupported file type: {file_extension}. Supported types are {list(MIME_TYPES.keys())}."
        )

    try:
        # Read the audio file
        with open(audio_file_path, "rb") as f:
            audio_bytes = f.read()

        model = genai.GenerativeModel("gemini-1.5-flash")

        # background thread
        response = await to_thread(model.generate_content, [
            "Identify the language spoken in this audio. Only return the ISO 639-1 code like 'en' or 'hi'.",
            {"mime_type": mime_type, "data": audio_bytes}
        ])

        # Extract the detected language
        detected_language = response.candidates[0].content.parts[0].text.strip()

        # Extract token usage metadata
        prompt_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        total_tokens = response.usage_metadata.total_token_count

        # Calculate the total cost using the imported helper function
        total_cost = calculate_cost(prompt_tokens, output_tokens)

        return ProviderResult(
            provider="Google Gemini",
            detected_language=detected_language,
            time_taken=time.time() - start_time,
            estimated_cost={"tokens": total_tokens, "dollars": total_cost},
            status="success"
        )
    except genai.APIError as e:
        # Handle specific API-related errors
        error_message = f"Gemini API Error: {e}"
        return ProviderResult(
            provider="Google Gemini",
            detected_language=None,
            time_taken=time.time() - start_time,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="error",
            error_message=error_message
        )
    except Exception as e:
        # Handle any other unexpected errors
        error_message = f"An unexpected error occurred: {e}"
        return ProviderResult(
            provider="Google Gemini",
            detected_language=None,
            time_taken=time.time() - start_time,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="error",
            error_message=error_message
        )
