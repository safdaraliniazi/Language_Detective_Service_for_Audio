import os
import time
import httpx
from app.models import ProviderResult
from dotenv import load_dotenv
load_dotenv()

# Load API key 
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_URL = "https://api.sarvam.ai/speech-to-text"

# MIME
MIME_TYPES = {
    ".m4a": "audio/x-m4a",
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".flac": "audio/flac",
    # etc etc
}

async def detect_language_sarvam(audio_file_path: str) -> ProviderResult:
    """
    Detects the language of an audio file using the Sarvam AI Speech-to-Text API.

    This function sends an audio file to the Sarvam AI endpoint and parses the
    response to extract the detected language code. It handles API key validation,
    file reading, and various network and HTTP errors.

    Args:
        audio_file_path (str): The local file path to the audio file.

    Returns:
        ProviderResult: A dataclass containing the provider name, detected language,
                        time taken, estimated cost, and status.
    """
    start_time = time.time()

    # --- 1. Initial Validation ---
    if not SARVAM_API_KEY:
        return ProviderResult(
            provider="Sarvam AI",
            detected_language=None,
            time_taken=0,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="error",
            error_message="SARVAM_API_KEY environment variable is not set."
        )

    # Determine the MIME type from the file extension
    file_extension = os.path.splitext(audio_file_path)[1].lower()
    mime_type = MIME_TYPES.get(file_extension)

    if not mime_type:
        return ProviderResult(
            provider="Sarvam AI",
            detected_language=None,
            time_taken=time.time() - start_time,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="error",
            error_message=f"Unsupported file type: {file_extension}. Supported types are {list(MIME_TYPES.keys())}."
        )

    try:
        # --- 2. API Call ---
        # Read the file and prepare the payload for the POST request
        with open(audio_file_path, "rb") as f:
            files = {"file": (os.path.basename(audio_file_path), f, mime_type)}
            headers = {"api-subscription-key": SARVAM_API_KEY}

            # Use httpx.AsyncClient for asynchronous network requests
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(SARVAM_URL, headers=headers, files=files)
                # This will raise an exception for 4xx and 5xx responses
                r.raise_for_status()
                data = r.json()

        # --- 3. Result Processing ---
        detected_language = data.get("language_code")

        # The Sarvam API response does not include token usage or cost,
        # so we default these values to zero.
        return ProviderResult(
            provider="Sarvam AI",
            detected_language=detected_language,
            time_taken=time.time() - start_time,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="success"
        )

    # --- 4. Error Handling ---
    except httpx.HTTPStatusError as e:
        # Handle specific HTTP error codes (e.g., 401, 404, 500)
        error_message = f"HTTP Error: {e.response.status_code} - {e.response.text}"
        return ProviderResult(
            provider="Sarvam AI",
            detected_language=None,
            time_taken=time.time() - start_time,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="error",
            error_message=error_message
        )
    except httpx.RequestError as e:
        # Handle network-related errors (e.g., DNS resolution, connection refused)
        error_message = f"Network Error: {e}"
        return ProviderResult(
            provider="Sarvam AI",
            detected_language=None,
            time_taken=time.time() - start_time,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="error",
            error_message=error_message
        )
    except Exception as e:
        # Catch any other unexpected exceptions
        error_message = f"An unexpected error occurred: {str(e)}"
        return ProviderResult(
            provider="Sarvam AI",
            detected_language=None,
            time_taken=time.time() - start_time,
            estimated_cost={"tokens": 0, "dollars": 0},
            status="error",
            error_message=error_message
        )
