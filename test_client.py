import asyncio
import os
from pathlib import Path
from fastmcp import Client
import logging
from dotenv import load_dotenv

# Load environment variables from .env file in the same directory as this script
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Setup basic logging to suppress unnecessary output
logging.basicConfig(level=logging.ERROR)

# Path to the data directory
DATA_DIR = Path(__file__).parent / "data"

async def run_tests():
    """
    Test script to transcribe all audio files in the data directory.
    Iterates through the data directory and attempts to transcribe each file.
    """
    print("=" * 60)
    print("Voxtral MCP - Audio Transcription Test Suite")
    print("=" * 60)
    
    if not os.environ.get("MISTRAL_API_KEY"):
        print("⚠️  WARNING: MISTRAL_API_KEY environment variable is not set.")
        print("   The tests will likely fail unless the API key is provided.")
        print("-" * 60)

    # Initialize the client pointing to our server.py
    # This will start the server in a subprocess
    client = Client("server.py")
    
    # Get list of audio files
    extensions = ["*.m4a", "*.mp3", "*.wav", "*.ogg", "*.flac"]
    audio_files = []
    for ext in extensions:
        audio_files.extend(DATA_DIR.glob(ext))
    
    # Sort files for consistent output
    audio_files.sort()
    
    if not audio_files:
        print(f"No audio files found in {DATA_DIR}")
        print(f"Please put some audio files in {DATA_DIR} and try again.")
        return

    print(f"Found {len(audio_files)} files to process.\n")
    
    async with client:
        # Check if the expected tool is available
        try:
            tools = await client.list_tools()
            tool_names = [t.name for t in tools]
            if "transcribe_audio" not in tool_names:
                print(f"❌ Error: Tool 'transcribe_audio' not found on server.")
                print(f"   Available tools: {tool_names}")
                return
        except Exception as e:
            print(f"❌ Error connecting to server: {e}")
            return

        passed = 0
        failed = 0

        for audio_path in audio_files:
            file_name = audio_path.name
            print(f"Processing: {file_name}")
            
            try:
                # Call the tool
                # Using 'text' format for simpler output in this test script
                result = await client.call_tool(
                    "transcribe_audio", 
                    {
                        "file_path": str(audio_path.absolute()),
                        "response_format": "text"
                    }
                )
                
                # Check for content in the response
                if hasattr(result, 'content') and result.content:
                    text_content = result.content[0].text
                    
                    # Our tool returns "Error: ..." strings for internal failures
                    if text_content.startswith("Error:"):
                        print(f"  ❌ FAILED: {text_content}")
                        failed += 1
                    else:
                        # Success! Show a snippet
                        preview = text_content[:150].strip().replace("\n", " ")
                        print(f"  ✅ SUCCESS!")
                        print(f"     Transcript: \"{preview}...\"")
                        passed += 1
                else:
                    print(f"  ❓ UNKNOWN: No content returned for {file_name}")
                    failed += 1
                    
            except Exception as e:
                print(f"  💥 EXCEPTION: {type(e).__name__}")
                print(f"     Details: {str(e)}")
                failed += 1
            
            # Wait 5 seconds between files
            if audio_path != audio_files[-1]:
                print("  (Waiting 5 seconds before next file...)")
                await asyncio.sleep(5)
            
            print("-" * 40)

        print("\n" + "=" * 60)
        print(f"Test Results: {passed} Passed, {failed} Failed")
        print("=" * 60)

if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\nTests interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred while running the tests: {e}")
