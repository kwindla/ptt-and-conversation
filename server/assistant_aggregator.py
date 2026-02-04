from __future__ import annotations

from pipecat.frames.frames import (
    LLMContextAssistantTimestampFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    TextFrame,
)
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import LLMAssistantAggregator
from pipecat.utils.time import time_now_iso8601


class PassthroughAssistantAggregator(LLMAssistantAggregator):
    def __init__(self, context: LLMContext):
        super().__init__(context=context)
        self._streaming_message_index: int | None = None

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)

        if isinstance(frame, (LLMFullResponseStartFrame, LLMFullResponseEndFrame, TextFrame)):
            await self.push_frame(frame, direction)

    async def _handle_llm_start(self, frame: LLMFullResponseStartFrame):
        await super()._handle_llm_start(frame)
        self._streaming_message_index = None

    async def _handle_text(self, frame: TextFrame):
        await super()._handle_text(frame)
        if not self._started or not frame.append_to_context or len(frame.text) == 0:
            return

        message = self._get_or_create_streaming_message()
        # Ensure spacing matches the aggregator's canonical output.
        message["content"] = self.aggregation_string()

    async def _handle_interruptions(self, frame):
        await super()._handle_interruptions(frame)
        self._streaming_message_index = None

    async def _handle_end_or_cancel(self, frame):
        await super()._handle_end_or_cancel(frame)
        self._streaming_message_index = None

    def _get_or_create_streaming_message(self) -> dict:
        messages = self._context.get_messages()

        if self._streaming_message_index is not None:
            if self._streaming_message_index < len(messages):
                existing = messages[self._streaming_message_index]
                if (
                    isinstance(existing, dict)
                    and existing.get("role") == "assistant"
                    and isinstance(existing.get("content"), str)
                ):
                    return existing
            self._streaming_message_index = None

        if messages:
            last = messages[-1]
            if (
                isinstance(last, dict)
                and last.get("role") == "assistant"
                and isinstance(last.get("content"), str)
            ):
                self._streaming_message_index = len(messages) - 1
                return last

        new_message = {"role": "assistant", "content": ""}
        new_index = len(messages)
        self._context.add_message(new_message)
        self._streaming_message_index = new_index
        return new_message

    async def push_aggregation(self) -> str:
        if not self._aggregation:
            return ""

        aggregation = self.aggregation_string()
        self._aggregation = []

        messages = self._context.get_messages()
        if self._streaming_message_index is not None and self._streaming_message_index < len(
            messages
        ):
            existing = messages[self._streaming_message_index]
            if (
                isinstance(existing, dict)
                and existing.get("role") == "assistant"
                and isinstance(existing.get("content"), str)
            ):
                existing["content"] = aggregation
            else:
                self._context.add_message({"role": "assistant", "content": aggregation})
        else:
            self._context.add_message({"role": "assistant", "content": aggregation})

        self._streaming_message_index = None

        await self.push_context_frame()

        timestamp_frame = LLMContextAssistantTimestampFrame(timestamp=time_now_iso8601())
        await self.push_frame(timestamp_frame)

        return aggregation
