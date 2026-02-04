# PTT and Conversation

A voice chat application featuring **push-to-talk** and **live conversation** modes, built with [Pipecat](https://github.com/pipecat-ai/pipecat) and the [Pipecat Voice UI Kit](https://github.com/pipecat-ai/voice-ui-kit).

## Features

- **Push-to-Talk Mode** — Hold a button to speak, release to send. Great for noisy environments or precise control.
- **Live Conversation Mode** — Natural back-and-forth conversation with automatic turn detection.
- **Text Input** — Type messages when you can't speak aloud. Auto-submits on Enter.
- **Krisp Noise Reduction** — Toggle AI-powered noise cancellation on/off.
- **Real-time Transcription** — See what you and the assistant are saying.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Client (React + Vite)                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Conversation│  │ Text Input  │  │ PTT / Mic Controls  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │ WebRTC / Daily
┌───────────────────────────▼─────────────────────────────────┐
│  Server (Pipecat Pipeline)                                  │
│  ┌─────┐  ┌─────┐  ┌─────────┐  ┌─────┐  ┌───────────────┐  │
│  │ STT │→ │ LLM │→ │ Context │→ │ TTS │→ │ Audio Output  │  │
│  └─────┘  └─────┘  └─────────┘  └─────┘  └───────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

**Services used:**
- **STT:** Deepgram (Nova 2)
- **LLM:** Anthropic (Claude Haiku)
- **TTS:** ElevenLabs (HTTP Flash v2.5)

---

## Quick Start

### 1. Set up environment variables

Create a `.env` file in the project root:

```bash
# Required
DEEPGRAM_API_KEY=your_deepgram_key
ANTHROPIC_API_KEY=your_anthropic_key
ELEVENLABS_API_KEY=your_elevenlabs_key
# Optional ElevenLabs settings:
# ELEVENLABS_VOICE_ID=JBFqnCBsd6RMkjVDRZzb
# ELEVENLABS_MODEL=eleven_flash_v2_5
```

### 2. Start the server

```bash
cd server
uv run python bot.py --transport webrtc
```

The server runs on `http://localhost:7860`.

### 3. Start the client

```bash
cd client
echo "VITE_LOCAL_WEBRTC_URL=http://localhost:7860/api/offer" > .env.local
npm install
npm run dev
```

The client runs on `http://localhost:5173`.

### 4. Connect and chat!

1. Click **Connect** to start a session
2. Choose your mode:
   - **PTT Mode:** Hold the circular button to speak
   - **Live Mode:** Just talk naturally
3. Type in the text box if you prefer typing
4. Toggle Krisp on/off in the header for noise reduction

## Project Structure

```
├── client/                 # React frontend
│   ├── src/
│   │   ├── App.tsx         # Main UI layout
│   │   ├── App.css         # Styling
│   │   ├── components/     # PTTButton, MicButton, ModeToggle, KrispToggle
│   │   └── hooks/          # useVoiceChatState
│   └── api/                # Vercel serverless functions
│       └── start-session.ts
│
├── server/                 # Pipecat bot
│   ├── bot.py              # Main bot pipeline
│   ├── frames.py           # Custom frame types
│   ├── turn_strategies.py  # PTT-aware turn detection
│   └── dynamic_krisp_filter.py
│
└── .env                    # API keys (create this)
```

----

## Pipecat Cloud

See: [https://docs.pipecat.ai/getting-started/quickstart](https://docs.pipecat.ai/getting-started/quickstart)

## How It Works

### Mode Switching

The client sends `ptt-mode-change` messages to switch between modes. In PTT mode, the bot only responds after the user releases the talk button. In Live mode, it uses Krisp VIVA for natural turn detection.

### Text Input

Text messages are sent via the RTVI `send-text` action, which:
1. Interrupts any current bot speech
2. Injects the message into the LLM context
3. Triggers a spoken response

### Krisp Integration

(Only on Pipecat Cloud)

The `DynamicKrispVivaFilter` can be toggled on/off at runtime via `krisp-control` messages, allowing users to disable noise reduction when needed.

---

## License

MIT
