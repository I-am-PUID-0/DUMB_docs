---
title: AI Assistant API
icon: lucide/brain
---

# AI Assistant API

The AI API manages provider settings and service diagnostics. Authentication follows the same DUMB API authentication behavior as the rest of the backend.

The backend makes provider requests from inside the DUMB container. Use provider URLs that are reachable from that container, not just from your browser.

## `GET /api/ai/settings`

Returns the active AI settings without exposing the stored API key.

Response includes `api_key_configured: true` when a key is stored.

## `PUT /api/ai/settings`

Updates the `dumb.ai` settings block. Omit `api_key` to keep the existing stored key.

Example payload:

```json
{
  "enabled": true,
  "provider": "ollama",
  "base_url": "http://127.0.0.1:11434",
  "model": "llama3.1",
  "max_log_chars": 20000,
  "include_logs": true,
  "include_service_config": true,
  "include_dependency_graph": true
}
```

Settings fields:

| Field | Description |
| --- | --- |
| `enabled` | Allows non-dry-run provider calls. Dry-run previews work even when this is false. |
| `provider` | `ollama`, `open_webui`, `openai`, `openai_compatible`, `compatible`, `litellm`, `anthropic`, or `claude`. |
| `base_url` | Provider endpoint reachable from the DUMB backend container. |
| `model` | Provider model name. |
| `api_key` | Optional for local providers; required for hosted OpenAI/Anthropic modes. Omit to preserve a stored key. |
| `timeout_sec` | Provider request timeout, clamped by the backend. |
| `temperature` | Provider temperature setting. |
| `max_log_chars` | Default maximum recent log characters included in diagnostic bundles. |
| `include_logs` | Default for including redacted service logs. |
| `include_service_config` | Default for including redacted service config. |
| `include_dependency_graph` | Default for including dependency graph context. |
| `include_docs_context` | Default for including selected DUMB_docs snippets in diagnostic bundles. |
| `include_process_list` | Default for including compact stack status context. |
| `max_docs_chars` | Maximum documentation characters included across selected docs snippets. |

## `POST /api/ai/test`

Tests the configured provider using a short connectivity prompt. The request can include unsaved provider fields, so the frontend can test current form values before saving them.

This endpoint does not include service logs, service configuration, dependency graph data, or diagnostic bundle content.

Example payload:

```json
{
  "provider": "ollama",
  "base_url": "http://ollama:11434",
  "model": "llama3.1",
  "timeout_sec": 60
}
```

Response fields:

| Field | Description |
| --- | --- |
| `ok` | True when the provider returned a response. |
| `provider` | Provider used for the test. |
| `model` | Model used for the test. |
| `response` | Provider response text. |
| `usage` | Best-effort token usage reported by the provider, when available. |

## `POST /api/ai/models`

Lists available models for providers with a compatible model-list endpoint. The request can include unsaved provider fields.

Supported discovery modes:

| Provider | Endpoint called from the DUMB backend |
| --- | --- |
| `ollama` | `{base_url}/api/tags` |
| `open_webui` | `{base_url}/api/models` |
| `openai` | `https://api.openai.com/v1/models` unless a custom base URL is provided |
| `litellm` | `{base_url}/models` |
| `openai_compatible` / `compatible` | `{base_url}/models` |

Example payload:

```json
{
  "provider": "ollama",
  "base_url": "http://ollama:11434",
  "timeout_sec": 60
}
```

Example response:

```json
{
  "provider": "ollama",
  "models": [
    {
      "name": "llama3.1:latest",
      "size": 4661224676,
      "modified_at": "2026-06-18T00:00:00Z"
    }
  ]
}
```

## `POST /api/ai/diagnose`

Builds a redacted service diagnostic bundle. If `dry_run` is true, or if AI is disabled, the endpoint returns the bundle without calling a provider. If AI is enabled and `dry_run` is false, DUMB sends the bundle to the configured provider and returns the analysis.

Use `dry_run: true` before enabling provider calls to inspect the exact bundle that would be shared.

Example payload:

```json
{
  "process_name": "Traefik Proxy Admin",
  "question": "Why is this service failing during startup?",
  "dry_run": true,
  "include_logs": true,
  "include_service_config": true,
  "include_dependency_graph": true,
  "include_docs_context": true,
  "max_log_chars": 20000
}
```

Response fields:

| Field | Description |
| --- | --- |
| `enabled` | Whether provider calls are enabled. |
| `provider` | Configured provider. |
| `model` | Configured model. |
| `analysis` | Provider response, empty for dry runs. |
| `bundle` | Redacted diagnostic bundle. |
| `usage` | Best-effort token usage reported by the provider, empty for dry runs or providers that do not return usage. |
| `dry_run` | True when no provider call was made. |

### Diagnostic Bundle Context

The bundle can include `docs_context` when `include_docs_context` is enabled. This block contains selected DUMB_docs excerpts with source paths and public documentation URLs. The backend chooses snippets using the service/config key, status, question text, and included logs.

DUMB prefers local Markdown from `DUMB_DOCS_PATH` or common sibling-repo workbench paths. If local docs are unavailable, it falls back to the matching public pages on `https://dumbarr.com`.

The bundle also includes DUMB product facts. API clients can use dry-run responses to verify that `dumb_product.expansion` is `Debrid Unlimited Media Bridge` before sending a provider request.

## `POST /api/ai/diagnose-stack`

Builds a stack-wide diagnostic bundle. Use this when the question is about the whole deployment instead of one service.

If `dry_run` is true, or if AI is disabled, the endpoint returns the bundle without calling a provider. If AI is enabled and `dry_run` is false, DUMB sends the stack bundle to the configured provider and returns the analysis.

Example payload:

```json
{
  "question": "What is blocking startup?",
  "dry_run": true,
  "include_logs": true,
  "include_service_config": false,
  "include_dependency_graph": true,
  "include_docs_context": true,
  "include_process_list": true,
  "max_log_chars": 20000,
  "max_docs_chars": 12000
}
```

Stack bundles include:

| Field | Description |
| --- | --- |
| `scope` | Always `stack`. |
| `stack_summary` | Status counts plus services needing attention. |
| `processes` | Compact process list when enabled. |
| `dumb_service_catalog` | DUMB-specific workflow guidance used for planning questions such as Usenet service selection. |
| `dependency_graph` | Aggregated runtime dependency graph across enabled services when enabled. |
| `logs` | Short targeted log tails for services needing attention when enabled. |
| `service_configs` | Optional redacted configs for enabled services. Disabled by default for stack requests. |
| `docs_context` | Selected DUMB_docs snippets when enabled and available. |

When `dry_run` is false, DUMB compacts stack bundles before sending them to the provider. The API response still includes the full built bundle, but the provider prompt uses shortened docs excerpts, targeted log snippets, capped graph nodes/edges, and omits full service configs with a note. This avoids common context-length failures with local models.

Provider responses include a `usage` object when the provider reports token or evaluation counts. OpenAI-compatible providers usually return `prompt_tokens`, `completion_tokens`, and `total_tokens`. Ollama native responses return `prompt_eval_count` and `eval_count`; DUMB maps those to prompt/completion/total token fields and preserves timing fields such as `total_duration`.

### Deterministic Finalizers

For selected stack questions, DUMB may post-process the provider response before returning `analysis`:

- Product identity questions such as `What does DUMB stand for?` return the canonical product fact, `Debrid Unlimited Media Bridge`, even if the provider invents another acronym expansion.
- DUMB Usenet planning questions are grounded around Decypharr, NzbDAV, AltMount, Arr apps, Prowlarr, and rclone. If a provider recommends SABnzbd, NZBGet, or NZBHydra as the primary DUMB path, DUMB replaces that with the DUMB-native workflow answer.

The original diagnostic bundle remains available in the response for review. Token `usage` still reflects the provider request when a provider call was made.
