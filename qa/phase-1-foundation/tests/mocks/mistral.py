"""Mock for the Mistral Large LLM client.

The real system calls Mistral Large (via the ``mistralai`` SDK, orchestrated by
LlamaIndex) to synthesise a structured compliance answer from retrieved
regulation chunks. This mock reproduces the surface of ``mistralai.Mistral`` so
tests never hit the network, stay deterministic, and can assert on exactly what
was sent to the model.

Design goals
------------
* **No hard dependency** on the ``mistralai`` package — the response objects are
  light dataclasses that quack like the SDK's (``resp.choices[0].message.content``).
* **Programmable**: queue exact responses, or register prompt-substring matchers,
  or fall back to a deterministic default compliance JSON.
* **Observable**: every call is recorded so tests can assert model name,
  messages, temperature, etc. (matters for the "no hallucinated laws" checks).
* **Sync and async**: exposes ``.chat.complete`` and ``.chat.complete_async``.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# --- SDK-compatible response shapes -----------------------------------------


@dataclass
class _Message:
    role: str
    content: str


@dataclass
class _Choice:
    message: _Message
    index: int = 0
    finish_reason: str = "stop"


@dataclass
class _Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ChatCompletionResponse:
    """Mirrors mistralai.models.ChatCompletionResponse closely enough for tests."""

    choices: list[_Choice]
    model: str = "mistral-large-latest"
    id: str = "mock-cmpl-0001"
    object: str = "chat.completion"
    usage: _Usage = field(default_factory=_Usage)

    @property
    def text(self) -> str:
        return self.choices[0].message.content


@dataclass
class RecordedCall:
    model: str
    messages: list[dict[str, Any]]
    kwargs: dict[str, Any]


# --- Default canned answer ---------------------------------------------------

DEFAULT_COMPLIANCE_ANSWER: dict[str, Any] = {
    "answer": (
        "AI-generated media is permitted under EU law but is subject to "
        "transparency obligations. Providers must disclose synthetic content "
        "under Article 50(2) of the EU AI Act."
    ),
    "regulationRefs": [
        {
            "regulation": "EU AI Act",
            "article": "Article 50(2)",
            "url": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj",
        },
        {
            "regulation": "GDPR",
            "article": "Article 22",
            "url": "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        },
    ],
    "rationale": "Synthesised from retrieved AI Act and GDPR chunks.",
}


def _default_content(messages: list[dict[str, Any]]) -> str:
    return json.dumps(DEFAULT_COMPLIANCE_ANSWER)


class _ChatNamespace:
    """Implements the ``client.chat.complete(...)`` access pattern."""

    def __init__(self, parent: MockMistralClient) -> None:
        self._parent = parent

    def complete(
        self, *, model: str, messages: list[dict[str, Any]], **kwargs: Any
    ) -> ChatCompletionResponse:
        return self._parent._respond(model=model, messages=messages, **kwargs)

    async def complete_async(
        self, *, model: str, messages: list[dict[str, Any]], **kwargs: Any
    ) -> ChatCompletionResponse:
        return self._parent._respond(model=model, messages=messages, **kwargs)


class MockMistralClient:
    """Drop-in stand-in for ``mistralai.Mistral``.

    Examples
    --------
    Default deterministic compliance JSON::

        llm = MockMistralClient()
        resp = llm.chat.complete(model="mistral-large-latest",
                                 messages=[{"role": "user", "content": "..."}])
        data = json.loads(resp.text)

    Queue exact responses (consumed FIFO)::

        llm.queue_response('{"answer": "..."}')

    Match on prompt content (useful for RAG eval fixtures)::

        llm.register("right to erasure", '{"regulationRefs": [...]}')

    Force a failure to test error handling / issuance retries::

        llm.fail_next(RuntimeError("Mistral API 503"))
    """

    def __init__(
        self,
        api_key: str | None = "mock-key",
        default_response: str | Callable[[list[dict[str, Any]]], str] | None = None,
    ) -> None:
        self.api_key = api_key
        self.chat = _ChatNamespace(self)
        self.calls: list[RecordedCall] = []

        self._queue: list[str] = []
        self._matchers: list[tuple[str, str]] = []
        self._pending_error: Exception | None = None
        self._default = default_response or _default_content

    # -- programming the mock -------------------------------------------------

    def queue_response(self, content: str) -> MockMistralClient:
        """Add a raw response string to the FIFO queue."""
        self._queue.append(content)
        return self

    def queue_json(self, payload: dict[str, Any]) -> MockMistralClient:
        return self.queue_response(json.dumps(payload))

    def register(self, prompt_substring: str, content: str) -> MockMistralClient:
        """Return ``content`` whenever the last user message contains the substring."""
        self._matchers.append((prompt_substring, content))
        return self

    def fail_next(self, error: Exception) -> MockMistralClient:
        """Raise ``error`` on the next call (then clear)."""
        self._pending_error = error
        return self

    def reset(self) -> None:
        self.calls.clear()
        self._queue.clear()
        self._matchers.clear()
        self._pending_error = None

    # -- helpers --------------------------------------------------------------

    @property
    def call_count(self) -> int:
        return len(self.calls)

    @property
    def last_messages(self) -> list[dict[str, Any]]:
        return self.calls[-1].messages if self.calls else []

    def _last_user_text(self, messages: list[dict[str, Any]]) -> str:
        for msg in reversed(messages):
            if msg.get("role") == "user":
                return str(msg.get("content", ""))
        return ""

    # -- core -----------------------------------------------------------------

    def _respond(
        self, *, model: str, messages: list[dict[str, Any]], **kwargs: Any
    ) -> ChatCompletionResponse:
        self.calls.append(RecordedCall(model=model, messages=messages, kwargs=kwargs))

        if self._pending_error is not None:
            err, self._pending_error = self._pending_error, None
            raise err

        content: str | None = None
        if self._queue:
            content = self._queue.pop(0)
        else:
            user_text = self._last_user_text(messages)
            for substring, resp in self._matchers:
                if substring.lower() in user_text.lower():
                    content = resp
                    break

        if content is None:
            content = self._default(messages) if callable(self._default) else self._default

        prompt_tokens = sum(len(str(m.get("content", "")).split()) for m in messages)
        completion_tokens = len(content.split())
        return ChatCompletionResponse(
            choices=[_Choice(message=_Message(role="assistant", content=content))],
            model=model,
            usage=_Usage(prompt_tokens, completion_tokens, prompt_tokens + completion_tokens),
        )
