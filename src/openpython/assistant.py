"""Small, dependency-free client for OpenAI-compatible chat-completions APIs."""

from __future__ import annotations

import ipaddress
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener, urlopen
from typing import Optional

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
LOCAL_BASE_URL = "http://127.0.0.1:11434/v1"
LOCAL_MODEL = "qwen2.5-coder:7b"
SYSTEM_PROMPT = """You are Openpython, a concise Python coding assistant inside a Jupyter notebook.
Answer with only the Python code needed for the user's request. Do not use Markdown
fences or add prose. Prefer clear, notebook-friendly code. Do not assume variables
or files exist unless the user mentioned them. Never include secrets in the answer."""


class OpenPythonError(RuntimeError):
    """An actionable configuration, network, or provider error."""


def _is_loopback_http(url: str) -> bool:
    try:
        parsed = urlsplit(url)
        address = ipaddress.ip_address(parsed.hostname or "")
        return parsed.scheme == "http" and address.is_loopback and not parsed.username and not parsed.password
    except ValueError:
        return False


class _LoopbackRedirectHandler(HTTPRedirectHandler):
    """Prevent a local endpoint from redirecting a local-only request outward."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _is_loopback_http(newurl):
            raise OpenPythonError("Local-only mode blocked a redirect away from loopback HTTP.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _credential_path() -> Path:
    override = os.getenv("OPENPYTHON_CONFIG_DIR")
    if override:
        directory = Path(override).expanduser()
    elif sys.platform == "win32":
        directory = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")) / "Openpython"
    else:
        directory = Path.home() / ".config" / "openpython"
    return directory / "credentials.json"


def _write_private_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        os.chmod(path.parent, 0o700)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(data, stream)
    if os.name != "nt":
        os.chmod(path, 0o600)


def get_local_only() -> bool:
    """Read the fail-closed local-only preference, with env override."""
    env_value = os.getenv("OPENPYTHON_LOCAL_ONLY")
    if env_value is not None:
        return env_value.strip().lower() not in {"", "0", "false", "no", "off"}
    try:
        data = json.loads((_credential_path().parent / "settings.json").read_text(encoding="utf-8"))
        return bool(data.get("local_only", False)) if isinstance(data, dict) else False
    except (OSError, ValueError):
        return False


def save_local_only(enabled: bool) -> None:
    """Persist the local-only choice for later notebook kernels on this machine."""
    _write_private_json(_credential_path().parent / "settings.json", {"local_only": bool(enabled)})


def get_api_key() -> Optional[str]:
    """Return the key from the environment or this user's local config file."""
    key = os.getenv("OPENPYTHON_API_KEY") or os.getenv("OPENAI_API_KEY")
    if key:
        return key
    try:
        data = json.loads(_credential_path().read_text(encoding="utf-8"))
        key = data.get("OPENPYTHON_API_KEY") if isinstance(data, dict) else None
        return key if isinstance(key, str) and key else None
    except (OSError, ValueError):
        return None


def save_api_key(key: str) -> None:
    """Persist a key in a per-user config file with owner-only POSIX permissions."""
    _write_private_json(_credential_path(), {"OPENPYTHON_API_KEY": key})


def delete_saved_api_key() -> None:
    """Remove the locally saved key, if present."""
    try:
        _credential_path().unlink()
    except FileNotFoundError:
        pass


def _configuration() -> tuple[str, str, Optional[str]]:
    local_only = get_local_only()
    default_url = LOCAL_BASE_URL if local_only else DEFAULT_BASE_URL
    default_model = LOCAL_MODEL if local_only else DEFAULT_MODEL
    base_url = os.getenv("OPENPYTHON_BASE_URL", default_url).strip().rstrip("/")
    model = os.getenv("OPENPYTHON_MODEL", default_model).strip()
    if not base_url or not model:
        raise OpenPythonError("OPENPYTHON_BASE_URL and OPENPYTHON_MODEL cannot be empty.")
    if local_only and not _is_loopback_http(base_url):
        raise OpenPythonError(
            "Local-only mode blocks all non-loopback or HTTPS model URLs. Configure an HTTP "
            "loopback endpoint such as http://127.0.0.1:11434/v1."
        )
    # A hosted API key is never sent to a local inference server.
    api_key = None if local_only else get_api_key()
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

    local_only = get_local_only()
    base_url, model, api_key = _configuration()
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    # Do not advertise a Jupyter/Openpython-specific User-Agent or add a Referer.
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = Request(
        f"{base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        if local_only:
            response_context = build_opener(ProxyHandler({}), _LoopbackRedirectHandler()).open(request, timeout=timeout)
        else:
            response_context = urlopen(request, timeout=timeout)
        with response_context as response:
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
