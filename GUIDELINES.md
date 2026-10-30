# Openpython usage guidelines

A practical guide for using Openpython in Jupyter notebooks. Openpython sends your prompt directly from the notebook kernel to the configured AI provider. It does not inspect or upload the rest of your notebook automatically.

## 1. Install and start

Use the current kernel in Jupyter and run the bootstrap line from the [README](README.md#install-and-start-in-one-notebook-line). It installs or upgrades Openpython and loads the notebook commands. You need Python 3.9+, Git, and internet access for the install and hosted API requests.

The first time you ask for code, Openpython prompts for your provider API key with hidden input and saves it locally for later sessions. The key is not stored in the notebook or repository. On POSIX systems the credential file is restricted to the current user; it is still plain text, so protect your computer account. Each person needs their own provider key. API usage may be billed by the provider.

After a kernel restart, load the extension again by running the bootstrap line, or—if Openpython is already installed—run:

```python
%load_ext openpython
```

## 2. Generate code

For a short request, use the line magic:

```python
%openpython create a pandas DataFrame with numbers 1 through 10 and their squares
```

For a longer request, use a cell magic and write the task in the cell body:

```python
%%openpython
Read `sales.csv` into a DataFrame named `sales`. Parse `order_date` as a date,
then plot monthly revenue with a title and labeled axes.
```

Openpython displays the generated Python; it does **not** execute it by default. Review the output, then copy it into a regular notebook cell if you want to edit it before running.

To run generated code immediately in the current kernel, explicitly use `--run`:

```python
%%openpython --run
Create a DataFrame named `squares` with numbers 1 through 10 and their squares.
```

Only use `--run` when you trust the task and provider. Generated code executes with the notebook kernel's permissions and can read files, access the network, or change data. For unfamiliar code, generate without `--run`, inspect it, and execute it yourself.

## 3. Get better results

- State the goal and the expected result: table, plot, file, calculation, or function.
- Include relevant variable names, column names, types, units, and constraints. Openpython does not automatically know your earlier cells or variables.
- Name libraries you want used (or avoided), and say whether you want a reusable function or a quick notebook snippet.
- Keep requests focused. Ask for one task at a time, then refine the result with another short request.
- If an answer assumes a missing import, variable, package, or file, mention what is available and ask for a corrected version.

Example of a focused prompt:

```text
Using the existing DataFrame `df` with columns `date` and `revenue`, plot monthly revenue.
Do not modify `df`; label both axes and handle missing dates.
```

## 4. Protect data and credentials

- Your prompt is sent to the configured AI provider. Do not include passwords, API keys, private customer data, or confidential notebook contents unless you are authorized to share them with that provider.
- Generated code is untrusted until reviewed. Be especially careful with file deletion/overwriting, shell commands, package installs, network calls, credential access, and database writes.
- Never put an API key in a notebook cell, prompt, source file, or public repository. Openpython stores the key in a user-local config file. On shared or temporary notebook machines, use a private account and remove the key when finished.
- Use `%openpython --set-key` to replace the saved key. Use `%openpython --forget-key` to remove the locally saved key and clear key variables from the current kernel.

## 5. Provider settings

OpenAI is the default provider and uses `gpt-4o-mini`. To use another OpenAI-compatible provider, set its base URL/model/key in the notebook **before** requesting code:

```python
import os
os.environ["OPENPYTHON_BASE_URL"] = "https://provider.example/v1"
os.environ["OPENPYTHON_MODEL"] = "your-model-name"
os.environ["OPENPYTHON_API_KEY"] = "your-key"
```

Set a provider key without putting it in notebook source by running `%openpython --set-key` in a separate cell; it uses hidden input and saves the key locally. Openpython accepts `OPENAI_API_KEY` as an environment-variable alias.

For a local Ollama server that exposes the OpenAI-compatible API, configure it like this:

```python
import os
os.environ["OPENPYTHON_BASE_URL"] = "http://localhost:11434/v1"
os.environ["OPENPYTHON_MODEL"] = "qwen2.5-coder:7b"
```

Ollama must already be running and the model must be available. `localhost` means the machine running the notebook kernel.

## 6. Common issues

- **`%openpython` is not recognized:** run `%load_ext openpython` in the current kernel. If the package is not installed, rerun the README bootstrap line.
- **Authentication error / HTTP 401:** check the provider key and model. Replace the key with `%openpython --set-key`; restart the kernel if you changed environment settings.
- **Connection or timeout error:** check that the kernel machine—not only your browser—can reach the provider and that the base URL is correct.
- **Rate limit / HTTP 429:** wait and retry, or check your provider quota and billing settings.
- **Package updated but old behavior remains:** restart the kernel, then load the extension again.
- **Need command help:** run `%openpython --help`.
