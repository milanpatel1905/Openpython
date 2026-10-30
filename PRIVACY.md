# Privacy notes

Openpython is designed to send a single request at a time. The request payload contains the Openpython instruction and the prompt you provide for that request. The package does not automatically collect or transmit previous notebook cells, outputs, variables, datasets, or IPython input history, and it does not maintain a multi-turn chat transcript.

## What still leaves the notebook

The current prompt is sent over HTTPS to the AI provider configured for your kernel. The provider processes it and may retain or log it according to the provider's terms and settings. Openpython cannot control or guarantee the provider's retention, access, or training policies. Do not send confidential material unless the provider and your organization's rules permit it.

## Hide prompt text from the notebook cell

Normal line and cell magics are written in the notebook source and may be saved by Jupyter. For a one-off task, use:

```python
%openpython --private
```

Enter the task at the hidden prompt. The task is not included in the cell source or normal IPython input history, but it is still sent to the configured provider. Use this only if your Jupyter frontend actually masks the input; cancel if it warns that input may be echoed.

Generated code appears in notebook output and may be saved with the notebook. Review it before execution, and clear cell outputs before saving/sharing if they contain sensitive information. Jupyter server owners, account administrators, and anyone who can access the notebook file may see saved notebook content.

## Keep requests on your own machine

To avoid sending prompts to a hosted provider, configure a local OpenAI-compatible model server (for example, Ollama) and point Openpython to its local endpoint. The local server must be running on, or reachable from, the machine running the notebook kernel. Verify that the model server does not forward prompts to a third party. Local use does not prevent other users or administrators with access to your computer from seeing notebook files or process data.
