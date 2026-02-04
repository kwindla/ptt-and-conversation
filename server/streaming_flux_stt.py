#
# Streaming Flux STT Service
#
# Extends DeepgramFluxSTTService to push InterimTranscriptionFrames during speech,
# enabling real-time transcription display in the UI.
#

from pipecat.frames.frames import InterimTranscriptionFrame
from pipecat.services.deepgram.flux.stt import DeepgramFluxSTTService
from pipecat.utils.time import time_now_iso8601


class StreamingFluxSTTService(DeepgramFluxSTTService):
    """DeepgramFluxSTTService with streaming interim transcriptions.

    The base DeepgramFluxSTTService receives Update events with partial transcripts
    but only logs them. This subclass pushes InterimTranscriptionFrames so clients
    can display real-time transcription progress.
    """

    async def _handle_update(self, transcript: str):
        """Handle Update events by pushing interim transcription frames.

        Args:
            transcript: The current partial transcript text for the ongoing turn.
        """
        if transcript:
            await self.push_frame(
                InterimTranscriptionFrame(
                    transcript,
                    self._user_id,
                    time_now_iso8601(),
                    self._language,
                )
            )
            await self._call_event_handler("on_update", transcript)
