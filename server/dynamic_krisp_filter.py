#
# Dynamic Krisp VIVA Filter
#
# Extends KrispVivaFilter to support runtime enable/disable via FilterUpdateSettingsFrame.
# This allows RTVI clients to toggle noise reduction without modifying pipecat-core.
#
# Note: Krisp VIVA requires the krisp_audio module which is only available in Pipecat Cloud.
# When running locally, this module provides a no-op fallback.
#

from loguru import logger

from pipecat.audio.filters.base_audio_filter import BaseAudioFilter
from pipecat.frames.frames import FilterControlFrame, FilterUpdateSettingsFrame

# Try to import KrispVivaFilter
try:
    from pipecat.audio.filters.krisp_viva_filter import KrispVivaFilter

    _KRISP_AVAILABLE = True
except Exception:
    _KRISP_AVAILABLE = False
    logger.warning("Krisp VIVA not available - using passthrough filter (Krisp requires Pipecat Cloud)")


if _KRISP_AVAILABLE:

    class DynamicKrispVivaFilter(KrispVivaFilter):
        """KrispVivaFilter with runtime enable/disable via FilterUpdateSettingsFrame."""

        async def process_frame(self, frame: FilterControlFrame):
            await super().process_frame(frame)

            if isinstance(frame, FilterUpdateSettingsFrame):
                if "enable" in frame.settings:
                    enabled = bool(frame.settings["enable"])
                    self._filtering = enabled
                    logger.info(f"Krisp VIVA filtering {'enabled' if enabled else 'disabled'}")

else:

    class DynamicKrispVivaFilter(BaseAudioFilter):
        """Passthrough filter when Krisp is not available (local development)."""

        def __init__(self):
            super().__init__()
            self._enabled = True

        async def start(self, sample_rate: int):
            self._sample_rate = sample_rate
            logger.debug(f"Passthrough filter started (sample_rate={sample_rate})")

        async def stop(self):
            logger.debug("Passthrough filter stopped")

        async def filter(self, audio: bytes) -> bytes:
            # Pass through audio unchanged
            return audio

        async def process_frame(self, frame: FilterControlFrame):
            await super().process_frame(frame)

            if isinstance(frame, FilterUpdateSettingsFrame):
                if "enable" in frame.settings:
                    enabled = bool(frame.settings["enable"])
                    self._enabled = enabled
                    logger.info(f"Krisp control received (enable={enabled}) but Krisp not available locally")
