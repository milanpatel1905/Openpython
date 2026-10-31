# Openpython

A small Jupyter/IPython helper for asking an AI provider to write Python code from the notebook. It sends the current request directly from the active kernel to an OpenAI-compatible API; it does not send previous cells or notebook history automatically, open a browser, start a web server, or install a frontend extension. The provider receives the current prompt and may retain it under its own policies. See the [usage guidelines](GUIDELINES.md) for privacy details, safe prompting, key management, and troubleshooting.

> **An internet connection is not an AI service or an API key.** For hosted models, provide your own provider API key. Alternatively, point Openpython at a local OpenAI-compatible service such as Ollama. Provider usage may incur charges.

## Install and start in one notebook line

Run this once in a Jupyter cell (it installs this GitHub project into the *current kernel* and activates the magic commands):

```python
import sys, subprocess; subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', '-U', 'git+https://github.com/milanpatel1905/Openpython.git@arena/9137e036-openpython']); get_ipython().run_line_magic('load_ext', 'openpython')
```

The cell prints a ready message. No browser, terminal, notebook extension setup, or long prompt is needed. You do need a working network connection to install from GitHub and to reach a hosted model.

## Configure a hosted model

OpenAI is the default provider (`gpt-4o-mini`). On your first request, Openpython asks for your API key using a masked prompt and saves it in a user-local config file, so you won't need to re-enter it on this computer. The key is not written into your notebook or repository; the file is plain text with owner-only permissions on POSIX systems. Keep your computer account private, or run `%openpython --forget-key` to remove the saved key. Use `%openpython --set-key` to replace it. You must already have a provider account and key, and provider usage may cost money. You can also set `OPENAI_API_KEY` instead of `OPENPYTHON_API_KEY`. To use another OpenAI-compatible provider, configure these environment variables **before** asking for code:

- `OPENPYTHON_BASE_URL`: provider API base URL, e.g. `https://api.example.com/v1`
- `OPENPYTHON_MODEL`: model identifier expected by that provider
- `OPENPYTHON_API_KEY`: provider key, if required

For local-only use, start Ollama with the model available, then run `%openpython --local-only`. This saves a fail-closed setting: Openpython will use `http://127.0.0.1:11434/v1` and `qwen2.5-coder:7b` by default and reject external model URLs. The Ollama server must be running on the machine running the notebook kernel (not necessarily the browser's machine). Use `%openpython --hosted` only when you want to re-enable remote provider requests.

## Privacy

Openpython sends only the current prompt, not earlier notebook history. The kernel calls the provider directly; no page is opened or added to browser URL history. Network services may still see connection metadata, and the provider receives the prompt and may log it. Jupyter saves cell source/output in notebooks. Use `%openpython --private` to type a request without placing it in the cell source; the request is still sent to the provider. See [Privacy notes](PRIVACY.md) for details.

## Use it

Generate a short request directly from a cell:

```python
%openpython plot a labeled histogram of the values in my_data
```

Or provide a longer request as the body of a cell:

```python
%%openpython
Load sales.csv into a pandas DataFrame, parse the date column, and plot monthly revenue.
```

Generated Python is displayed in the output and **is not run by default**. To explicitly execute the generated code in the current notebook kernel, use:

```python
%%openpython --run
Create a pandas DataFrame with the first ten square numbers and display it.
```

Only use `--run` for code you trust: generated code executes with the same permissions as your notebook. `%openpython --help` shows the command summary. The prompt is sent to your configured provider; do not include private or sensitive data unless you are comfortable sharing it with that provider.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Agent/skill design reference

This project was built with reference to the open-source [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code) agent and skill collection, particularly its [Python reviewer](https://github.com/affaan-m/everything-claude-code/blob/main/agents/python-reviewer.md), [Python patterns](https://github.com/affaan-m/everything-claude-code/blob/main/skills/python-patterns/SKILL.md), [Python testing](https://github.com/affaan-m/everything-claude-code/blob/main/skills/python-testing/SKILL.md), and [security review](https://github.com/affaan-m/everything-claude-code/blob/main/skills/security-review/SKILL.md) material. ECC is an inspiration/reference, not a runtime dependency; this package does not bundle its agents or skills.

## License

MIT
