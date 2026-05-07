import os
from typing import Optional, List, Union
from fastmcp import FastMCP
from openai import OpenAI
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voxtral-mcp")

# Debug: Print if key is found (masked)
api_key = os.environ.get("MISTRAL_API_KEY")
if api_key:
    masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "****"
    logger.info(f"MISTRAL_API_KEY found: {masked_key}")
else:
    logger.warning("MISTRAL_API_KEY not found in environment or .env file.")

# Initialize FastMCP server
mcp = FastMCP("Voxtral")

# Initialize OpenAI client with Mistral base URL
# It will look for MISTRAL_API_KEY in environment variables
def get_client():
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        logger.warning("MISTRAL_API_KEY not found in environment. Please set it.")
    
    return OpenAI(
        api_key=api_key or "dummy_key",
        base_url="https://api.mistral.ai/v1"
    )

client = get_client()

@mcp.tool()
async def transcribe_audio(
    file_path: str, 
    model: str = "voxtral-mini-latest",
    language: Optional[str] = None,
    diarize: bool = False,
    response_format: str = "json"
) -> str:
    """
    Transcribe an audio file (mp3, m4a, wav, etc.) using Mistral's Voxtral model.
    
    Args:
        file_path: Absolute path to the audio file.
        model: The Mistral model to use (default: voxtral-mini-latest).
        language: Optional ISO language code (e.g., 'en', 'fr', 'es').
        diarize: Whether to include speaker diarization (boolean).
        response_format: Format of the response ('json', 'text', 'verbose_json', 'srt', 'vtt').
    """
    path = Path(file_path).expanduser()
    if not path.is_file():
        return f"Error: File not found or not a file at {file_path}"
    
    try:
        # Refresh client if API key was set after initialization
        global client
        if client.api_key == "dummy_key":
            client = get_client()
            
        with open(path, "rb") as audio_file:
            # Mistral-specific features like diarization are passed via extra_body 
            # if not directly supported by the standard OpenAI SDK parameters
            # Although 'timestamp_granularities' is supported by OpenAI SDK, 
            # Mistral's 'diarize' is a custom field.
            
            extra_body = {}
            if diarize:
                extra_body["diarize"] = True
            
            # Note: Mistral's /audio/transcriptions endpoint
            # Pattern: -F model="voxtral-mini-latest" -F file=@file.mp3
            
            # Determine which parameters to send
            params = {
                "model": model,
                "file": audio_file,
                "response_format": response_format,
            }
            
            if language:
                params["language"] = language
            
            if response_format == "verbose_json":
                # Mistral supports 'word' and 'segment' for timestamps
                params["timestamp_granularities"] = ["word", "segment"]
                
            if extra_body:
                params["extra_body"] = extra_body

            logger.info(f"Transcribing {file_path} with model {model}...")
            
            # Using the synchronous client inside an async tool is fine for simple cases,
            # but we could use aiohttp or wrap in run_in_executor if needed.
            # FastMCP handles async tool execution.
            
            response = client.audio.transcriptions.create(**params)
            
            if response_format == "text":
                return response
            elif response_format in ["srt", "vtt"]:
                return response
            elif response_format == "json":
                return response.text
            else:
                # verbose_json returns a Transcription object or dict
                if hasattr(response, 'model_dump_json'):
                    return response.model_dump_json(indent=2)
                return str(response)

    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        return f"Error during transcription: {str(e)}"

if __name__ == "__main__":
    mcp.run()
