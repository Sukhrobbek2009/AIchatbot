from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from dataclasses import dataclass

from google import genai
from google.genai import types

from .config import Config

log = logging.getLogger(__name__)

# Finish reasons that mean the model/safety filters declined to answer.
_BLOCKED = {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII", "IMAGE_SAFETY", "IMAGE_PROHIBITED_CONTENT"}


@dataclass
class Result:
    text: str
    truncated: bool = False
    refused: bool = False


def _parts(content) -> list[types.Part]:
    """Plain string, or a list of {'type': 'text'|'bytes', ...} blocks -> Gemini parts."""
    if isinstance(content, str):
        return [types.Part.from_text(text=content)]
    parts = []
    for b in content:
        if b["type"] == "bytes":
            parts.append(types.Part.from_bytes(data=b["data"], mime_type=b["mime"]))
        else:
            parts.append(types.Part.from_text(text=b["text"]))
    return parts


class AI:
    def __init__(self, cfg: Config) -> None:
        self.cfg = cfg
        self.client = genai.Client(api_key=cfg.gemini_api_key)

    async def generate(
        self,
        *,
        system: str,
        messages: list[dict],
        max_tokens: int,
        on_text: Callable[[str], Awaitable[None]],
    ) -> Result:
        """Stream a reply, calling on_text for every text delta."""
        contents = [
            types.Content(role="model" if m["role"] == "assistant" else "user", parts=_parts(m["content"]))
            for m in messages
        ]
        config = types.GenerateContentConfig(
            system_instruction=system,
            max_output_tokens=max_tokens,
        )
        text, finish, blocked = "", None, False
        stream = await self.client.aio.models.generate_content_stream(
            model=self.cfg.model, contents=contents, config=config
        )
        async for chunk in stream:
            if chunk.prompt_feedback and chunk.prompt_feedback.block_reason:
                blocked = True
            for cand in chunk.candidates or []:
                if cand.finish_reason:
                    finish = getattr(cand.finish_reason, "name", str(cand.finish_reason))
            delta = chunk.text or ""
            if delta:
                text += delta
                await on_text(delta)
        log.info("finish=%s chars=%d", finish, len(text))
        return Result(
            text=text,
            truncated=finish == "MAX_TOKENS",
            refused=(blocked or finish in _BLOCKED) and not text.strip(),
        )
