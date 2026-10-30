# Openpython

A small Jupyter/IPython helper for asking an AI provider to write Python code from the notebook. It sends a request directly from the active kernel to an OpenAI-compatible API; it does not open a browser, start a web server, or install a frontend extension.

> **An internet connection is not an AI service or an API key.** For hosted models, provide your own provider API key. Alternatively, point Openpython at a local OpenAI-compatible service such as Ollama. Provider usage may incur charges.

## Install and start in one notebook line

Run this once in a Jupyter cell (it installs this GitHub project into the *current kernel* and activates the magic commands):

```python
import subprocess, sys; subprocess.check_call([sys.executable, "-m", "pip", "-q", "install", "git+https://github.com/milanpatel1905/Openpython.git@arena/9137e036-openpython"]); import openpython; openpython.start()
```

The cell prints a ready message. No browser, terminal, notebook extension setup, or long prompt is needed. You do need a working network connection to install from GitHub and to reach a hosted model.

## Configure a hosted model

Set a key in the kernel without saving it in the notebook source:

```python
import getpass, os; os.environ["OPENPYTHON_API_KEY"] = getpass.getpass("AI provider API key: ")
```

OpenAI is the default provider (`gpt-4o-mini`). You can also set `OPENAI_API_KEY` instead of `OPENPYTHON_API_KEY`. To use another OpenAI-compatible provider, configure these environment variables **before** asking for code:

- `OPENPYTHON_BASE_URL`: provider API base URL, e.g. `https://api.example.com/v1`
- `OPENPYTHON_MODEL`: model identifier expected by that provider
- `OPENPYTHON_API_KEY`: provider key, if required

For a local Ollama server exposing its OpenAI-compatible endpoint, for example:

```python
import os; os.environ["OPENPYTHON_BASE_URL"] = "http://localhost:11434/v1"; os.environ["OPENPYTHON_MODEL"] = "qwen2.5-coder:7b"
```

The Ollama server must be running and reachable **from the machine running the notebook kernel**. `localhost` refers to that machine, not the browser.

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
