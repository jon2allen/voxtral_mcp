# Voxtral MCP Server

An MCP server that provides high-quality audio transcription using Mistral's **Voxtral** models via the Mistral AI API.

## Features

- **Transcription**: Transcribe `mp3`, `m4a`, `wav`, `ogg`, `flac`, `webm`, and `opus` files.
- **Diarization**: Support for speaker diarization (speaker labels).
- **Multiple Formats**: Get results as plain text, JSON, Verbose JSON (with timestamps), SRT, or VTT.
- **Multilingual**: Supports 50+ languages.
- **OpenAI SDK Compatible**: Built using the OpenAI Python SDK for robust API interaction.
- ** not tested outside Mistral API 

## Installation

1. Clone or copy this directory to your machine.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set your Mistral API Key:
   ```bash
   export MISTRAL_API_KEY='your_api_key_here'
   ```

## Usage in Claude Desktop/Antigravity and others

Add the following to your `mcp_config.json` or other config file:

```json
{
  "mcpServers": {
    "voxtral": {
      "command": "python3",
      "args": ["/Users/jon2allen/github/voxtral_mcp/server.py"],
      "env": {
        "MISTRAL_API_KEY": "YOUR_MISTRAL_API_KEY"
      }
    }
  }
}
```

## Testing

A test script is provided to batch process audio files in the `data/` directory:

1. Place your audio files in the `data/` folder.
2. Run the test script:
   ```bash
   python3 test_client.py
   ```

The script will report the status of each transcription and provide a preview of the text for successful runs.

## Tools

### `transcribe_audio`
Transcribes an audio file.

**Parameters:**
- `file_path` (string, required): Absolute path to the audio file.
- `model` (string, optional): Mistral model to use. Default is `voxtral-mini-latest`.
- `language` (string, optional): ISO language code (e.g., `en`, `fr`).
- `diarize` (boolean, optional): Set to `true` for speaker diarization.
- `response_format` (string, optional): `text`, `json`, `verbose_json`, `srt`, or `vtt`. Default is `json`.

## Implementation Details

This server interfaces with the Mistral AI API endpoint `https://api.mistral.ai/v1/audio/transcriptions`. It uses the OpenAI Python SDK by overriding the `base_url`, as Mistral's audio API is compatible with the OpenAI transcription specification.

Special features like `diarize` are passed through the `extra_body` parameter of the SDK.

## License

MIT License

Copyright (c) 2026 Jon Allen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
