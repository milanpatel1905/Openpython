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

## Keep requests on your own machine

To avoid sending prompts to a hosted provider, configure a local OpenAI-compatible model server (for example, Ollama) and point Openpython to its local endpoint. The local server must be running on, or reachable from, the machine running the notebook kernel. Verify that the model server does not forward prompts to a third party. Local use does not prevent other users or administrators with access to your computer from seeing notebook files or process data.
