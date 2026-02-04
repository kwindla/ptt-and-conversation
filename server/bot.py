#
# PTT and Live Voice Conversation Bot
#
# Run locally:  uv run python bot.py --transport webrtc
# Run on Pipecat Cloud: uses --transport daily automatically
#

import os

import aiohttp

from dotenv import load_dotenv
from loguru import logger

from pipecat.frames.frames import FilterUpdateSettingsFrame, LLMRunFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMUserAggregator,
    LLMUserAggregatorParams,
)
from pipecat.processors.frameworks.rtvi import RTVIClientMessage
from pipecat.runner.types import RunnerArguments
from pipecat.runner.utils import create_transport
from pipecat.services.anthropic.llm import AnthropicLLMService
from streaming_flux_stt import StreamingFluxSTTService
from pipecat.services.elevenlabs.tts import ElevenLabsHttpTTSService
from pipecat.transports.base_transport import BaseTransport, TransportParams
from pipecat.transports.daily.transport import DailyParams

from frames import (
    PTTUserStartedSpeakingFrame,
    PTTUserStoppedSpeakingFrame,
    SwitchToLiveModeFrame,
    SwitchToPTTModeFrame,
)
from turn_strategies import PTTAwareUserTurnStrategies
from dynamic_krisp_filter import DynamicKrispVivaFilter
from assistant_aggregator import PassthroughAssistantAggregator

# Load .env from parent directory (where it currently exists)
load_dotenv(dotenv_path="../.env", override=True)

transport_params = {
    "webrtc": lambda: TransportParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        audio_in_filter=DynamicKrispVivaFilter(),
    ),
    "daily": lambda: DailyParams(
        audio_in_enabled=True,
        audio_out_enabled=True,
        audio_in_filter=DynamicKrispVivaFilter(),
    ),
}


async def run_bot(transport: BaseTransport, runner_args: RunnerArguments):
    logger.info("Starting bot")

    http_session: aiohttp.ClientSession = aiohttp.ClientSession()

    stt = StreamingFluxSTTService(
        api_key=os.getenv("DEEPGRAM_API_KEY"),
    )

    llm = AnthropicLLMService(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-haiku-4-5",
    )

    tts = ElevenLabsHttpTTSService(
        api_key=os.getenv("ELEVENLABS_API_KEY"),
        aiohttp_session=http_session,
        model="eleven_flash_v2_5",
        voice_id="JBFqnCBsd6RMkjVDRZzb",
    )

    system_message = {
        "role": "system",
        "content": (
            "You are a helpful voice assistant. Keep responses concise and conversational. "
            "Avoid special characters that can't be spoken aloud."
        ),
    }

    context = LLMContext([system_message])

    # Custom turn strategy for switchable PTT and live modes
    turn_strategies = PTTAwareUserTurnStrategies()

    user_aggregator = LLMUserAggregator(
        context,
        params=LLMUserAggregatorParams(user_turn_strategies=turn_strategies),
    )

    # Aggregator subclass that adds to the context token-by-token. (Didn't we have
    # one of these in the core library before?)
    assistant_aggregator = PassthroughAssistantAggregator(context)

    pipeline = Pipeline(
        [
            transport.input(),
            stt,
            user_aggregator,
            llm,
            assistant_aggregator,
            tts,
            transport.output(),
        ]
    )

    task = PipelineTask(
        pipeline,
        params=PipelineParams(
            enable_metrics=True,
            enable_usage_metrics=True,
        ),
        idle_timeout_secs=runner_args.pipeline_idle_timeout_secs,
    )

    # Track current mode for validation (starts in PTT mode)
    current_mode = "ptt"

    @task.rtvi.event_handler("on_client_message")
    async def on_client_message(processor, message: RTVIClientMessage):
        nonlocal current_mode

        if message.type == "ptt-mode-change":
            new_mode = message.data.get("mode")
            if new_mode not in ("live", "ptt"):
                await processor.send_error_response(message, f"Invalid mode: {new_mode}")
                return

            # Interrupt any ongoing bot speech for clean mode transition
            await processor.interrupt_bot()

            # Queue mode switch frame - strategies will handle the switch
            if new_mode == "live":
                await task.queue_frame(SwitchToLiveModeFrame())
            else:
                await task.queue_frame(SwitchToPTTModeFrame())

            current_mode = new_mode
            logger.info(f"Mode changed to: {current_mode}")
            await processor.send_server_response(message, {"mode": current_mode})

        elif message.type == "ptt-state":
            if current_mode != "ptt":
                logger.warning("Received ptt-state message but not in PTT mode")
                return

            speaking = message.data.get("speaking")
            if not isinstance(speaking, bool):
                await processor.send_error_response(message, "speaking must be a boolean")
                return

            if speaking:
                await processor.interrupt_bot()
                logger.debug("PTT: User started speaking")
                await task.queue_frame(PTTUserStartedSpeakingFrame())
            else:
                logger.debug("PTT: User stopped speaking")
                await task.queue_frame(PTTUserStoppedSpeakingFrame())

        elif message.type == "krisp-control":
            enable = message.data.get("enable", True)
            if not isinstance(enable, bool):
                await processor.send_error_response(message, "enable must be a boolean")
                return

            # Queue the settings frame into the pipeline to toggle Krisp filtering
            await task.queue_frame(FilterUpdateSettingsFrame(settings={"enable": enable}))
            logger.info(f"Krisp VIVA control: {'enabled' if enable else 'disabled'}")
            await processor.send_server_response(message, {"enabled": enable})

    @transport.event_handler("on_client_connected")
    async def on_client_connected(transport, client):
        logger.info("Client connected")
        # Greet the user with a one-shot user message that triggers the greeting
        # This doesn't bloat context since it's a normal conversational turn
        context.add_message({"role": "user", "content": "Hello!"})
        await task.queue_frames([LLMRunFrame()])

    @transport.event_handler("on_client_disconnected")
    async def on_client_disconnected(transport, client):
        logger.info("Client disconnected")
        await task.cancel()

    runner = PipelineRunner(handle_sigint=runner_args.handle_sigint)
    try:
        await runner.run(task)
    finally:
        if http_session is not None:
            await http_session.close()


async def bot(runner_args: RunnerArguments):
    """Main bot entry point compatible with Pipecat runner."""
    transport = await create_transport(runner_args, transport_params)
    await run_bot(transport, runner_args)


if __name__ == "__main__":
    from pipecat.runner.run import main

    main()
