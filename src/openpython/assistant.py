"""Small, dependency-free client for OpenAI-compatible chat-completions APIs."""

from __future__ import annotations

import json
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Optional

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = """You are Openpython, a concise Python coding assistant inside a Jupyter notebook.
Answer with only the Python code needed for the user's request. Do not use Markdown
fences or add prose. Prefer clear, notebook-friendly code. Do not assume variables
or files exist unless the user mentioned them. Never include secrets in the answer."""


class OpenPythonError(RuntimeError):
    """An actionable configuration, network, or provider error."""


def _configuration() -> tuple[str, str, Optional[str]]:
    base_url = os.getenv("OPENPYTHON_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
    model = os.getenv("OPENPYTHON_MODEL", DEFAULT_MODEL).strip()
    api_key = os.getenv("OPENPYTHON_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not base_url or not model:
        raise OpenPythonError("OPENPYTHON_BASE_URL and OPENPYTHON_MODEL cannot be empty.")
    if "api.openai.com" in base_url and not api_key:
        raise OpenPythonError(
            "No API key found. Set OPENPYTHON_API_KEY (or OPENAI_API_KEY) in the "
            "kernel environment, or configure an OpenAI-compatible local service. "
            "Internet access alone does not provide an AI API key."
        )
    return base_url, model, api_key


def _extract_code(content: str) -> str:
    """Accept a provider's occasional fenced response while returning plain code."""
    text = content.strip()
    match = re.fullmatch(r"```(?:python|py)?\s*\n?(.*?)\n?```", text, flags=re.I | re.S)
    if match:
        text = match.group(1).strip()
    if not text:
        raise OpenPythonError("The model returned an empty response. Try a more specific prompt.")
    return text


def generate_code(prompt: str, *, timeout: float = 60.0) -> str:
    """Generate Python code by making a direct request from this notebook kernel.

    Configuration uses OPENPYTHON_API_KEY, OPENPYTHON_BASE_URL, and
    OPENPYTHON_MODEL. OPENAI_API_KEY is accepted as a convenience alias.
    """
    prompt = prompt.strip()
    if not prompt:
        raise OpenPythonError("Add a short task after %openpython or in the cell body.")

    base_url, model, api_key = _configuration()
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    headers = {"Content-Type": "application/json", "User-Agent": "openpython-notebook/0.1"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        # Avoid including request headers or credentials in errors shown in notebook output.
        detail = exc.read(500).decode("utf-8", errors="replace")
        raise OpenPythonError(f"AI provider returned HTTP {exc.code}: {detail}") from None
    except (URLError, TimeoutError, OSError) as exc:
        raise OpenPythonError(
            f"Could not reach {base_url}. Check this kernel's internet connection and provider URL. ({exc})"
        ) from None
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise OpenPythonError(f"The AI provider returned invalid JSON: {exc}") from None

    try:
        content = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        raise OpenPythonError("The AI provider response did not contain a chat completion.") from None
    if not isinstance(content, str):
        raise OpenPythonError("The AI provider returned an unsupported response format.")
    return _extract_code(content)
