---
title: AI Assistant
icon: lucide/brain
---

# AI Assistant

DUMB includes an optional AI diagnostics assistant for service pages. It can collect a redacted runtime bundle for one service, preview that bundle, and optionally send it to a configured local or cloud model for troubleshooting guidance.

The frontend also includes **Stack AI Assist** for whole-stack questions. Use the service-page **AI Assist** tab when one service is the focus, and use **Stack AI Assist** when you want the assistant to reason across service status, dependency chains, selected logs, and docs context for the entire DUMB deployment.

The assistant is disabled by default. You can still use **Preview bundle** without enabling provider calls, which lets you inspect exactly what DUMB would share before using a model.

## Quick Setup

1. Open any service page in the DUMB frontend.
2. Select the **AI Assist** tab.
3. Choose a provider and model.
4. For Ollama or OpenAI-compatible providers, use **Load models** if you want DUMB to ask the provider for available model names.
5. Use **Test provider** to confirm the base URL, model, and API key work.
6. Use **Preview bundle** before enabling provider calls.
7. Confirm the redacted bundle only includes context you are comfortable sharing.
8. Enable **Provider calls**, save settings, then use **Analyze**.

!!! tip "Start local first"
    A local Ollama or OpenAI-compatible endpoint is the safest first test because logs and config context stay on your own machine or LAN.

## What It Can Use

Service diagnostic bundles can include:

- DUMB product facts, including the canonical expansion: Debrid Unlimited Media Bridge
- Current service status and health details
- Recent redacted service logs
- Redacted service configuration
- Backend dependency graph context
- Selected public DUMB documentation snippets
- Optional compact process list
- Your free-form question or troubleshooting focus

Stack diagnostic bundles can include:

- DUMB product facts, including the canonical expansion: Debrid Unlimited Media Bridge
- Stack-wide service status counts
- Services needing attention, grouped by unhealthy, stopped, or unknown state
- Compact process list for the included services
- Aggregated runtime dependency graph across enabled services
- Short targeted log tails for services needing attention
- Optional redacted configs for enabled services
- Selected public DUMB documentation snippets
- A small DUMB service catalog for workflow planning questions
- Your free-form stack question or troubleshooting focus

DUMB redacts common secret fields and sensitive log patterns before the bundle is returned or sent to a provider. This includes common API key, password, token, cookie, authorization, OAuth client secret, GitHub token, Plex token, and Cloudflare tunnel token fields.

### Docs Context

When **Include docs context** is enabled, DUMB adds a `docs_context` block to the preview/analyze bundle. The backend selects a small set of DUMB_docs Markdown pages based on:

- The current service/config key
- The service status
- Your question/focus text
- Included log text

Docs context is included in **Preview bundle**, so you can see exactly which pages and excerpts would be sent before using **Analyze**.

The backend looks for the docs directory in common dev/workbench locations and also honors `DUMB_DOCS_PATH`. If the docs directory is not mounted in the DUMB container, the bundle includes a note that docs were unavailable instead of silently omitting that fact.

## Providers

Supported provider modes:

| Provider | Use case | Notes |
| --- | --- | --- |
| Local Ollama | Private local diagnostics | Calls `/api/chat`. The base URL must be reachable from the DUMB backend container. |
| Open WebUI | Use models exposed through Open WebUI | Calls Open WebUI's `/api/chat/completions` and `/api/models`; requires an Open WebUI API key. |
| OpenAI | Hosted OpenAI models | Uses `/v1/chat/completions`; requires an API key. |
| OpenAI-compatible | Local or hosted compatible APIs | Set the base URL to the provider root, such as `http://localhost:1234/v1`. |
| LiteLLM | LiteLLM proxy/gateway deployments | Uses OpenAI-compatible `/chat/completions` and `/models`; set the base URL to the LiteLLM `/v1` root, such as `http://litellm:4000/v1`. |
| Anthropic / Claude | Hosted Claude models | Uses `/v1/messages`; requires an API key. |

### Container Reachability

The AI request is made by the DUMB backend, not by your browser. That means:

- `http://127.0.0.1:11434` points to the DUMB container itself.
- If Ollama runs as another container on the same Docker network, use that container name, for example `http://ollama:11434`.
- If the provider runs on the Docker host, use a host-reachable address from inside the DUMB container.
- For Open WebUI, set provider to **Open WebUI**, set the base URL to the Open WebUI root reachable from DUMB, for example `http://open-webui:3000`, and paste an Open WebUI API key.
- For LiteLLM, choose **LiteLLM** or **OpenAI-compatible**, set the base URL to the `/v1` root, and use the LiteLLM model alias from your proxy config.
- For OpenAI-compatible services such as LM Studio or LiteLLM, include the `/v1` base path when the provider expects OpenAI-style chat completions.

### Testing and Model Discovery

Use **Test provider** after entering the provider, base URL, model, and API key. This sends a short connectivity prompt only. It does not include service logs, service config, dependency graph data, or your diagnostic question.

When the provider reports usage, DUMB shows token counts with the provider test and analysis result. OpenAI-compatible providers usually report prompt, completion, and total tokens. Ollama reports prompt/eval counts and timing data; DUMB maps those into the same display where possible. Some providers or proxy layers may not return usage.

Use **Load models** to populate the model picker from providers that expose a simple model-list endpoint:

- Ollama: DUMB calls `{base_url}/api/tags`.
- Open WebUI: DUMB calls `{base_url}/api/models`.
- LiteLLM, OpenAI, and OpenAI-compatible providers: DUMB calls `{base_url}/models`.

When Open WebUI returns model metadata, DUMB labels discovered models as local, external, or unknown in the picker. This is best-effort because Open WebUI model metadata can differ by version and connection type.

Anthropic/Claude model discovery is not currently exposed by this DUMB UI; enter the model name manually.

### Testing Context Quality

Use **Preview bundle** to prove DUMB is collecting the right context before you judge a model response. Preview mode returns the redacted bundle without sending it to a provider.

Good context checks:

- Ask `What does DUMB stand for?` and confirm the bundle includes `dumb_product.expansion` as `Debrid Unlimited Media Bridge`.
- Ask `What services should I use for Usenet in DUMB?` and confirm the bundle includes `dumb_service_catalog`, `dumb_workflow_rules`, and docs snippets for Decypharr, NzbDAV, AltMount, Prowlarr, or core-service routing.
- Toggle **Docs context** off and on, then compare the preview bundle. With docs enabled, the bundle should include a `docs_context` block with source paths and excerpts.
- Keep **Include configs** off for broad stack planning until you specifically need redacted configuration details.

Then use **Analyze** with the same prompt. This separates two different checks:

- Preview proves DUMB is building the context correctly.
- Analyze proves whether the selected model follows that context.

Small local models may still lean on generic training data. To keep important answers stable, DUMB applies deterministic finalizers for selected product facts and workflow-planning traps. For example, DUMB pins the official acronym expansion and replaces generic Usenet advice that recommends SABnzbd, NZBGet, or NZBHydra as the primary DUMB path.

### Field Reference

| Field | What it does |
| --- | --- |
| **Enable provider calls** | Allows **Analyze** to send the redacted bundle to the configured provider. Leave this off when you only want preview mode. |
| **Include logs** | Adds recent redacted service log text. This is usually the most helpful context for startup failures. |
| **Include config** | Adds this service's redacted DUMB configuration. Secret-like keys are masked. |
| **Include dependency graph** | Adds backend-resolved dependency context, including missing or stopped upstream services. |
| **Include docs context** | Adds selected DUMB_docs snippets that match the service, question, status, and logs. |
| **Include compact process list** | Adds a compact status list for other services. Use it for stack-wide startup issues, but disable it if you only want single-service context. |
| **Base URL** | Provider endpoint reachable from the DUMB backend container. |
| **Model** | Model name sent to the provider. |
| **Load models** | Fetches available model names from Ollama or OpenAI-compatible providers. |
| **Test provider** | Sends a short connectivity prompt using the current provider settings. |
| **API key** | Stored in DUMB config. Leave blank when saving to keep an existing stored key unchanged. |
| **Log characters** | Maximum recent log characters included in the diagnostic bundle. |
| **Docs characters** | Maximum documentation characters included across selected snippets. |
| **Timeout seconds** | How long DUMB waits for the provider response. |

## Stack AI Assist

Open **Stack AI Assist** from the sidebar for whole-deployment troubleshooting. It uses the same provider settings as the service-page assistant, but the diagnostic bundle is built around the entire stack instead of one service.

Good stack-level questions include:

- "What is blocking startup?"
- "Which dependency chain should I fix first?"
- "Why are multiple services unhealthy?"
- "Does this look like a proxy, database, mount, or service config problem?"
- "What services should I use for Usenet?"
- "Should this stack use Decypharr, NzbDAV, AltMount, or a combined workflow?"

Stack preview mode is especially important when enabling optional configs. The compact process list, dependency graph, and docs context are normally useful, while **Include configs** should be enabled only when you need deeper cross-service config reasoning and have reviewed the preview.

For provider calls, Stack AI Assist compacts the preview bundle before sending it to the model. This keeps local models and Open WebUI/Ollama setups from failing on context length while preserving the full preview for operator review. Workflow-planning questions omit log tails from the provider prompt so the model focuses on DUMB service selection instead of generic troubleshooting. The effective context limit still depends on the selected model and its Ollama/Open WebUI runtime settings, so one model can reject a prompt that another model accepts with the same DUMB settings. If you need deep config or long-log analysis for one service, use that service's **AI Assist** tab.

Stack workflow prompts also include a DUMB-specific service catalog. For example, Usenet planning is grounded around DUMB services such as Decypharr, NzbDAV, AltMount, Arr apps, Prowlarr, and rclone instead of generic external download-client advice. If a provider returns a generic Usenet answer that recommends SABnzbd, NZBGet, or NZBHydra as the primary path, DUMB replaces it with the DUMB-native planning answer.

Product identity prompts are also guarded. If a provider invents a different acronym expansion, DUMB returns the canonical product fact instead: **Debrid Unlimited Media Bridge**.

## Configuration

Settings are stored under `dumb.ai` in `dumb_config.json`:

```json
"ai": {
  "enabled": false,
  "provider": "ollama",
  "base_url": "http://127.0.0.1:11434",
  "model": "",
  "api_key": "",
  "timeout_sec": 60,
  "temperature": 0.2,
  "max_log_chars": 20000,
  "include_logs": true,
  "include_service_config": true,
  "include_dependency_graph": true,
  "include_docs_context": true,
  "include_process_list": false,
  "max_docs_chars": 12000
}
```

In the frontend, open a service page and select **AI Assist**. Configure the provider, model, and context toggles, then save settings. Use **Preview bundle** first, then **Analyze** when provider calls are enabled.

### Examples

Local Ollama on the same Docker network:

```json
{
  "enabled": true,
  "provider": "ollama",
  "base_url": "http://ollama:11434",
  "model": "llama3.1"
}
```

OpenAI:

```json
{
  "enabled": true,
  "provider": "openai",
  "model": "gpt-4.1-mini",
  "api_key": "YOUR_OPENAI_API_KEY"
}
```

Anthropic / Claude:

```json
{
  "enabled": true,
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-latest",
  "api_key": "YOUR_ANTHROPIC_API_KEY"
}
```

OpenAI-compatible local or gateway provider:

```json
{
  "enabled": true,
  "provider": "openai_compatible",
  "base_url": "http://your-provider:1234/v1",
  "model": "your-model"
}
```

LiteLLM proxy:

```json
{
  "provider": "litellm",
  "base_url": "http://litellm:4000/v1",
  "model": "Local - Qwen 2.5 14B",
  "api_key": "optional-proxy-key"
}
```

Open WebUI:

```json
{
  "enabled": true,
  "provider": "open_webui",
  "base_url": "http://open-webui:3000",
  "model": "llama3.1",
  "api_key": "YOUR_OPEN_WEBUI_API_KEY"
}
```

## Privacy Notes

AI diagnostics are most useful when logs and config context are included, but those can contain deployment-specific details. Keep provider calls disabled if you only want local preview, use a local model for private analysis, and avoid enabling the compact process list unless the wider stack context is needed.

The assistant suggests next steps only. It does not apply configuration changes, restart services, or modify files.
