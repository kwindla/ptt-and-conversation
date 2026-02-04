#
# Custom frames for PTT and Live mode voice conversation
#

from dataclasses import dataclass

from pipecat.frames.frames import SystemFrame


# Mode switching frames
@dataclass
class SwitchToLiveModeFrame(SystemFrame):
    """Switch turn detection to live (Flux-controlled) mode."""

    pass


@dataclass
class SwitchToPTTModeFrame(SystemFrame):
    """Switch turn detection to PTT (manual) mode."""

    pass


# PTT state frames
@dataclass
class PTTUserStartedSpeakingFrame(SystemFrame):
    """Custom frame indicating PTT button was pressed."""

    pass


@dataclass
class PTTUserStoppedSpeakingFrame(SystemFrame):
    """Custom frame indicating PTT button was released."""

    pass
