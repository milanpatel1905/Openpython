# Openpython usage guidelines

A practical guide for using Openpython in Jupyter notebooks. Openpython sends only the current request to the configured AI provider; it does not read or send previous notebook cells, outputs, variables, or IPython history automatically. Separate requests are not added to an Openpython conversation history.

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

## 4. Privacy and credentials

Openpython does not transmit your notebook history or dataset automatically. A normal `%openpython ...` or `%%openpython` request is visible in the notebook cell and may be saved with the notebook. To enter a task without putting its text in the cell source or ordinary IPython input history, run:

```python
%openpython --private
```

Type the task into the hidden prompt. This keeps the prompt text out of the cell source, but **still sends that task to the configured AI provider**. Provider retention/logging depends on that provider's policies; Openpython cannot guarantee the provider will not retain or access a request. Jupyter may save generated output, and notebook server administrators or anyone with access to your account/files may be able to see saved notebooks. Clear outputs and avoid saving sensitive results if that is a concern. For data that must not leave your computer, use a local model endpoint (such as Ollama) reachable from the kernel, and verify that the model service itself does not forward requests elsewhere.

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

For local-only operation, install Ollama, make the model available, and run `%openpython --local-only`. This saves a local-only preference and uses the loopback endpoint `http://127.0.0.1:11434/v1` with `qwen2.5-coder:7b` by default. Ollama must be running on the same machine as the notebook kernel. Local-only mode rejects remote and HTTPS model URLs. Run `%openpython --hosted` to explicitly allow hosted requests again.

## 6. Common issues

- **`%openpython` is not recognized:** run `%load_ext openpython` in the current kernel. If the package is not installed, rerun the README bootstrap line.
- **Authentication error / HTTP 401:** check the provider key and model. Replace the key with `%openpython --set-key`; restart the kernel if you changed environment settings.
- **Connection or timeout error:** check that the kernel machine—not only your browser—can reach the provider and that the base URL is correct.
- **Rate limit / HTTP 429:** wait and retry, or check your provider quota and billing settings.
- **Package updated but old behavior remains:** restart the kernel, then load the extension again.
- **Need command help:** run `%openpython --help`.
