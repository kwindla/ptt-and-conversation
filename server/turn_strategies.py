#
# PTT-aware turn strategies for dual-mode voice conversation
#

from loguru import logger

from pipecat.frames.frames import Frame, UserStartedSpeakingFrame, UserStoppedSpeakingFrame
from pipecat.turns.user_start.base_user_turn_start_strategy import BaseUserTurnStartStrategy
from pipecat.turns.user_stop.external_user_turn_stop_strategy import ExternalUserTurnStopStrategy
from pipecat.turns.user_turn_strategies import UserTurnStrategies

from frames import (
    PTTUserStartedSpeakingFrame,
    PTTUserStoppedSpeakingFrame,
    SwitchToLiveModeFrame,
    SwitchToPTTModeFrame,
)


class PTTAwareUserTurnStartStrategy(BaseUserTurnStartStrategy):
    """Turn start strategy that supports both Live and PTT modes.

    - In Live mode: responds to UserStartedSpeakingFrame (from Flux)
    - In PTT mode: responds only to PTTUserStartedSpeakingFrame (from client)

    Mode is controlled via SwitchToLiveModeFrame and SwitchToPTTModeFrame.
    """

    def __init__(self, **kwargs):
        super().__init__(enable_interruptions=False, enable_user_speaking_frames=False, **kwargs)
        self._mode = "ptt"  # Start in PTT mode

    async def process_frame(self, frame: Frame):
        await super().process_frame(frame)

        # Handle mode switch frames
        if isinstance(frame, SwitchToLiveModeFrame):
            logger.debug("Turn start strategy: switching to live mode")
            self._mode = "live"
            return

        if isinstance(frame, SwitchToPTTModeFrame):
            logger.debug("Turn start strategy: switching to PTT mode")
            self._mode = "ptt"
            return

        # Handle turn start based on current mode
        if self._mode == "live":
            if isinstance(frame, UserStartedSpeakingFrame):
                await self.trigger_user_turn_started()
        else:  # PTT mode
            if isinstance(frame, PTTUserStartedSpeakingFrame):
                await self.trigger_user_turn_started()


class PTTAwareUserTurnStopStrategy(ExternalUserTurnStopStrategy):
    """Turn stop strategy that supports both Live and PTT modes.

    - In Live mode: responds to UserStoppedSpeakingFrame (from Flux)
    - In PTT mode: responds only to PTTUserStoppedSpeakingFrame (from client)

    Mode is controlled via SwitchToLiveModeFrame and SwitchToPTTModeFrame.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._mode = "ptt"  # Start in PTT mode

    async def process_frame(self, frame: Frame):
        # Handle mode switch frames
        if isinstance(frame, SwitchToLiveModeFrame):
            logger.debug("Turn stop strategy: switching to live mode")
            self._mode = "live"
            return

        if isinstance(frame, SwitchToPTTModeFrame):
            logger.debug("Turn stop strategy: switching to PTT mode")
            self._mode = "ptt"
            return

        # Handle PTT-specific frames (only in PTT mode)
        if isinstance(frame, PTTUserStartedSpeakingFrame):
            if self._mode == "ptt":
                await self._handle_user_started_speaking(frame)
            return

        if isinstance(frame, PTTUserStoppedSpeakingFrame):
            if self._mode == "ptt":
                await self._handle_user_stopped_speaking(frame)
            return

        # Handle standard frames (only in live mode)
        if isinstance(frame, UserStartedSpeakingFrame):
            if self._mode == "live":
                await self._handle_user_started_speaking(frame)
            return

        if isinstance(frame, UserStoppedSpeakingFrame):
            if self._mode == "live":
                await self._handle_user_stopped_speaking(frame)
            return

        # Let parent handle transcription frames
        await super().process_frame(frame)


class PTTAwareUserTurnStrategies(UserTurnStrategies):
    """Container for PTT-aware turn strategies."""

    def __init__(self):
        self.start = [PTTAwareUserTurnStartStrategy()]
        self.stop = [PTTAwareUserTurnStopStrategy()]
