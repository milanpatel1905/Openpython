# Privacy notes

Openpython is designed to send a single request at a time. The request payload contains the Openpython instruction and the prompt you provide for that request. The package does not automatically collect or transmit previous notebook cells, outputs, variables, datasets, or IPython input history, and it does not maintain a multi-turn chat transcript.

## What still leaves the notebook

The current prompt is sent over HTTPS to the AI provider configured for your kernel. This request is made by the notebook **kernel**, not by browser navigation: it does not open a page or add a URL to browser history. Openpython does not send a `Referer` or an Openpython/Jupyter-specific `User-Agent`; the HTTP library may still use its generic Python user-agent. The provider sees the API request and may associate it with your API account, process it, and retain/log it under its own terms and settings. Openpython cannot hide an API request from the provider or guarantee the provider will not log it.

HTTPS encrypts the request and response contents in transit, but your network, firewall, or proxy may still record the destination service and connection metadata (such as time and traffic volume). The current prompt is sent to the provider, so do not send confidential material unless the provider and your organization's rules permit it. For no hosted-provider request, use a local model endpoint and verify that it does not forward traffic elsewhere.

## Hide prompt text from the notebook cell

Normal line and cell magics are written in the notebook source and may be saved by Jupyter. For a one-off task, use:

```python
%openpython --private
```

Enter the task at the hidden prompt. The task is not included in the cell source or normal IPython input history, but it is still sent to the configured provider. Use this only if your Jupyter frontend actually masks the input; cancel if it warns that input may be echoed.

Generated code appears in notebook output and may be saved with the notebook. Review it before execution, and clear cell outputs before saving/sharing if they contain sensitive information. Jupyter server owners, account administrators, and anyone who can access the notebook file may see saved notebook content.

## Block external model requests

If you do not want Openpython to make an external HTTPS model request, run:

```python
%openpython --local-only
```

This preference is saved for later kernels on this computer. In this mode, Openpython defaults to `http://127.0.0.1:11434/v1` and `qwen2.5-coder:7b`. It **fails closed** if configured with a non-loopback or HTTPS model URL, never sends the saved hosted API key to the local model, and blocks redirects away from loopback HTTP. Run `%openpython --hosted` to explicitly re-enable hosted-provider requests.

A local OpenAI-compatible model server (for example Ollama) must be installed, running, and have the model downloaded. The inference request then goes only to the loopback address on the notebook-kernel machine; it is not sent to a hosted AI provider. If Jupyter runs on a remote server, install/run the model on that server or an appropriate local service reachable there.

This blocks Openpython's **model-generation** traffic, not installation or setup traffic: installing/upgrading from GitHub or downloading a model may still make internet/HTTPS requests. Do that beforehand, then use local-only mode. No software can guarantee that the operating system or local administrators do not record local activity, or prevent them from accessing notebook files/processes.
