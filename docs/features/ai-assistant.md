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
4. For Anthropic, Gemini, Ollama, OpenAI, or OpenAI-compatible providers, use **Load models** if you want DUMB to ask the provider for available model names.
5. Use **Test provider** to confirm the base URL, model, and API key work.
6. Enter a profile name and choose **Save profile** if you want to retain this provider alongside other local or cloud providers.
7. Use **Preview bundle** before enabling provider calls.
8. Confirm the redacted bundle only includes context you are comfortable sharing.
9. Enable **Provider calls**, save settings, then use **Analyze**.

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

## Evidence Over Time

AI Assist can compare a selected current window with the previous matching period or with the period before the latest configuration change saved through DUMB.

The generic collector works for every managed service and can include:

- Current status and health
- Bounded scans of current and rotated log files
- Error counts, recurring signatures, newly observed signatures, restart markers, and selected cited excerpts
- Process CPU, memory, disk activity, PID changes, and sample coverage from DUMB Metrics history
- Existing read-only Database Health evidence when that service is opted into monitoring
- A redacted timeline of settings changes plus API-driven start, stop, restart, and manual update events
- Backend dependency and documentation context

The evidence summary reports the exact time window, sources that were available, log files and bytes scanned, and a deterministic confidence hint. The model is instructed to cite timestamps and measurements, distinguish facts from correlations, and say when evidence is insufficient.

Deep log scanning is independent of the truncated frontend log table. The backend reads retained files directly within `max_log_scan_mb`, then includes aggregates and selected redacted excerpts. It does not give the model arbitrary filesystem access.

### NzbDAV Native Evidence

NzbDAV has an additional read-only native collector for the maintained `nzbdav/nzbdav` fork. When available, it reads the existing NzbDAV SQLite stores and queue logs to compare:

- Concurrent queue worker count and connection budget context
- Segment success, missing article, error, retry, and provider latency rates
- Read session volume, duration, and errors
- Queue completion/failure counts, long-running processors, first-segment timing, and busy-period throughput

These metrics do not measure Plex click-to-first-frame latency. AI Assist labels that limitation and treats before/after results as correlation unless a recorded setting change provides a known boundary.

Native collectors are allowlisted and read-only. Services without a native collector still receive the generic diagnostics above.

## Guided Workflow

Both service and stack assistants provide presets for health, performance, recent changes, errors, and dependencies. Choose a time window and baseline, preview the evidence, then analyze it.

Provider results render as sanitized Markdown, including tables. You can copy or download the report, download the redacted JSON bundle, and ask follow-up questions using a short-lived in-memory diagnostic session. Follow-ups reuse the same evidence instead of rescanning logs or silently changing the comparison window.

Sessions expire after one hour and are not written to disk. Starting a new backend process also clears them.

### Docs Context

When **Include docs context** is enabled, DUMB adds a `docs_context` block to the preview/analyze bundle. The backend selects a small set of DUMB_docs Markdown pages based on:

- The current service/config key
- The service status
- Your question/focus text
- Included log text

Docs context is included in **Preview bundle**, so you can see exactly which pages and excerpts would be sent before using **Analyze**.

Official DUMB images include a Markdown-only snapshot of DUMB_docs at `/usr/share/dumb/docs`; images and other documentation assets are excluded to keep the image-size increase small. The backend prefers `DUMB_DOCS_PATH`, then this bundled snapshot and common dev/workbench locations.

If no local docs are available, DUMB fetches the matching public page from `https://dumbarr.com`, extracts its article content, and removes navigation, scripts, page chrome, and whitespace-only lines before adding the excerpt. The raw page is processed in memory and is not cloned or cached to disk. If neither source is available, the bundle includes an explicit note instead of silently omitting docs context.

## Providers

Supported provider modes:

| Provider | Use case | Notes |
| --- | --- | --- |
| Local Ollama | Private local diagnostics | Calls `/api/chat`. The base URL must be reachable from the DUMB backend container. |
| Google Gemini | Hosted Gemini Developer API models | Calls Google's native `generateContent` API and model-list endpoint through a DUMB-managed official endpoint; requires a Gemini API key. Limited free-tier access is available for eligible models and regions. |
| Open WebUI | Use models exposed through Open WebUI | Calls Open WebUI's `/api/chat/completions` and `/api/models`; requires an Open WebUI API key. |
| OpenAI | Hosted OpenAI models | Uses DUMB's managed official OpenAI endpoint and the Responses API for text/Codex models; requires an API key. |
| OpenAI-compatible | Local or hosted compatible APIs | Set the base URL to the provider root, such as `http://localhost:1234/v1`. |
| LiteLLM | LiteLLM proxy/gateway deployments | Uses OpenAI-compatible `/chat/completions` and `/models`; set the base URL to the LiteLLM `/v1` root, such as `http://litellm:4000/v1`. |
| Anthropic / Claude | Hosted Claude models | Uses DUMB's managed official Anthropic `/v1/messages` endpoint and `/v1/models` discovery; requires an API key. |

### Saved Provider Profiles

AI Assist can save up to 20 named provider profiles. Each profile retains:

- Provider type
- Base URL, except for native Gemini, OpenAI, and Anthropic where DUMB manages the official endpoint
- Model
- API key
- Request timeout
- Temperature, where supported

Use **Saved provider** to activate a profile. Activation happens in the DUMB backend, reloads that profile's provider details into the form, and immediately updates both service-page AI Assist and Stack AI Assist. On every settings load, the active saved profile is authoritative over the backward-compatible top-level provider fields, preventing stale provider/model values from appearing beside a different selected profile. Selecting the already-active profile also reloads its stored values, which discards any unsaved form changes.

Changing a selected profile's name, endpoint, model, key, timeout, or temperature changes the **Saved provider** selector to **Unsaved provider** and shows which profile has unsaved changes. Choose **Update profile** to write those changes back to the original profile. Changing the provider type detaches it as a new provider instead, clears the old profile name/key state, and uses **Save profile** to create it.

Use **New** to explicitly start an unsaved profile from the values currently visible in the form, **Save profile** to create it, **Update profile** to update the profile being edited, and **Delete** to remove the currently selected saved profile. Saving general AI settings while the selector shows **Unsaved provider** preserves the saved profiles without overwriting them.

Provider-call enablement and evidence settings remain global. They are not duplicated per profile, so switching from a local Ollama profile to Gemini does not silently change which logs, configs, metrics, or docs are included.

Stored profile API keys are never returned by the AI settings API. The frontend receives only `api_key_configured`, and leaving the key field blank while saving preserves the existing stored key.

### Container Reachability

The AI request is made by the DUMB backend, not by your browser. That means:

- `http://127.0.0.1:11434` points to the DUMB container itself.
- If Ollama runs as another container on the same Docker network, use that container name, for example `http://ollama:11434`.
- For Gemini, DUMB always uses the official `https://generativelanguage.googleapis.com/v1beta` endpoint and does not expose it as an editable field. DUMB sends the key in the `x-goog-api-key` header rather than the URL.
- Native OpenAI and Anthropic also use managed official endpoints. Native OpenAI requests use `/v1/responses`; LiteLLM, Open WebUI, and generic OpenAI-compatible gateways continue using their Chat Completions compatibility routes. To route either model family through a gateway, select **LiteLLM** or **OpenAI-compatible** instead.
- If the provider runs on the Docker host, use a host-reachable address from inside the DUMB container.
- For Open WebUI, set provider to **Open WebUI**, set the base URL to the Open WebUI root reachable from DUMB, for example `http://open-webui:3000`, and paste an Open WebUI API key.
- For LiteLLM, choose **LiteLLM** or **OpenAI-compatible**, set the base URL to the `/v1` root, and use the LiteLLM model alias from your proxy config.
- For OpenAI-compatible services such as LM Studio or LiteLLM, include the `/v1` base path when the provider expects OpenAI-style chat completions.

### Testing and Model Discovery

Use **Test provider** after entering the provider, model, API key, and a base URL when that provider exposes one. This sends a short connectivity prompt only. It does not include service logs, service config, dependency graph data, or your diagnostic question.

When the provider reports usage, DUMB shows token counts with the provider test and analysis result. Gemini reports prompt, candidate, thought, and total token counts; DUMB maps prompt/candidate/total into the common display and preserves thought-token usage. OpenAI-compatible providers usually report prompt, completion, and total tokens. Ollama reports prompt/eval counts and timing data; DUMB maps those into the same display where possible. Some providers or proxy layers may not return usage.

Use **Load models** to populate the model picker from providers that expose a simple model-list endpoint:

- Ollama: DUMB calls `{base_url}/api/tags`.
- Gemini: DUMB calls the managed Google endpoint's `/models` route, filters for models that support `generateContent`, and removes the `models/` resource prefix before displaying names.
- Anthropic: DUMB calls the managed official `/v1/models?limit=1000` endpoint.
- Open WebUI: DUMB calls `{base_url}/api/models`.
- LiteLLM and OpenAI-compatible providers: DUMB calls `{base_url}/models`.
- OpenAI: DUMB calls the managed official OpenAI `/v1/models` endpoint.

When Open WebUI returns model metadata, DUMB labels discovered models as local, external, or unknown in the picker. This is best-effort because Open WebUI model metadata can differ by version and connection type.

Providers can continue returning model IDs that are retired, scheduled for retirement, or unsuitable for DUMB's text-diagnostics request path. DUMB keeps those entries visible so existing profiles remain understandable, but marks known retired models, scheduled shutdown dates, and unsupported non-text/specialized models. **Test provider** and **Analyze** are disabled for retired or incompatible selections, and the backend rejects those requests with replacement or compatibility guidance before contacting the provider.

The maintained catalog follows [Google's Gemini schedule](https://ai.google.dev/gemini-api/docs/deprecations), [OpenAI's deprecation schedule](https://developers.openai.com/api/docs/deprecations), and [Anthropic's model retirement schedule](https://platform.claude.com/docs/en/about-claude/model-deprecations). A weekly repository workflow compares the catalog with those official tables and fails when a supported text model is added or its date/replacement changes. Runtime model refresh still asks the configured provider every time; it is not a cached DUMB list.

Gemini model discovery remains the preferred way to choose a model because free-tier eligibility and model availability can differ by project, region, and current Google policy, but appearing in a provider response alone does not prove the model can accept DUMB's request type. Native OpenAI text and Codex models use the Responses API. Embedding, moderation, image/video, audio/realtime, and specialized tool-only OpenAI entries are marked unsupported for AI Assist rather than being sent to an incompatible endpoint.

### Gemini Free-Tier Setup

1. Create a Gemini API key in [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Restrict the key to Gemini API use and do not put it in logs, screenshots, or tracked config examples.
3. Select **Google Gemini** in AI Assist. DUMB manages the official Google API endpoint and starts with `gemini-3.5-flash-lite`.
4. Enter the key, select **Load models**, and choose a `generateContent` model actually returned for your project.
5. Use **Test provider**, then **Preview bundle**, before enabling provider calls.

The [Gemini API pricing page](https://ai.google.dev/gemini-api/docs/pricing) describes the current free and paid tiers. Free access is limited to certain models and changing quotas; active limits are shown in Google AI Studio. The free tier does not require DUMB-specific billing, but availability depends on Google's region and account rules. Google states that free-tier content may be used to improve its products, while paid-tier content is not used for that purpose. Treat any cloud-provider diagnostic request as a data disclosure even after DUMB redaction.

If Google returns `429` with a quota `limit: 0`, first check whether the selected model is marked retired. That response can mean the endpoint was shut down rather than that recent requests consumed an allowance.

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
| **Base URL** | Provider endpoint reachable from the DUMB backend container. Native Gemini, OpenAI, and Anthropic manage this automatically and hide the editable field. |
| **Model** | Model name sent to the provider. |
| **Load models** | Fetches current model names from Anthropic, Gemini, Ollama, OpenAI, or OpenAI-compatible providers and annotates known lifecycle/compatibility issues. |
| **Test provider** | Sends a short connectivity prompt using the current provider settings. |
| **API key** | Stored in DUMB config. Leave blank when saving to keep an existing stored key unchanged. |
| **Saved provider** | Activates a previously saved provider profile across service and stack AI Assist. |
| **Profile name** | Human-readable unique name for a saved provider configuration. |
| **New** | Starts an unsaved provider profile using the current visible provider values. |
| **Save profile** | Creates or updates the selected profile and makes it active. |
| **Update profile** | Writes unsaved edits back to the saved profile that populated the form and makes it active again. |
| **Delete** | Removes the selected profile. If it was active, DUMB activates the first remaining profile or returns to the default Ollama settings. |
| **Log characters** | Maximum recent log characters included in the diagnostic bundle. |
| **Deep-scan budget** | Maximum retained-log data read across current and rotated files. This bounds work; it does not reserve storage. |
| **Current window** | Period analyzed, from one hour through 30 days. Actual coverage depends on retained logs and Metrics history. |
| **Compare with** | Previous matching period, the period before the latest recorded change, or no baseline. |
| **Retained log scan** | Builds bounded aggregates and cited excerpts from retained log files. |
| **Metrics history** | Adds current-versus-baseline process measurements when DUMB Metrics history is available. |
| **Change history** | Adds redacted configuration changes saved through DUMB. |
| **Native telemetry** | Adds allowlisted read-only service evidence when a native collector exists. |
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
  "active_profile_id": "",
  "profiles": [],
  "timeout_sec": 60,
  "temperature": 0.2,
  "max_log_chars": 20000,
  "include_logs": true,
  "include_service_config": true,
  "include_dependency_graph": true,
  "include_docs_context": true,
  "include_process_list": false,
  "max_docs_chars": 12000,
  "diagnostic_window_hours": 24,
  "comparison_mode": "previous_period",
  "deep_log_scan": true,
  "max_log_scan_mb": 128,
  "include_metrics": true,
  "include_change_history": true,
  "include_native_diagnostics": true
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

Google Gemini free-tier starting point:

```json
{
  "enabled": true,
  "provider": "gemini",
  "model": "gemini-3.5-flash-lite",
  "api_key": "YOUR_GEMINI_API_KEY"
}
```

Use **Load models** instead of assuming that this example model remains available to every project.

Anthropic / Claude:

```json
{
  "enabled": true,
  "provider": "anthropic",
  "model": "claude-sonnet-4-6",
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

AI diagnostics are most useful when logs and config context are included, but those can contain deployment-specific details. Keep provider calls disabled if you only want local preview, use a local model for private analysis, and avoid enabling the compact process list unless the wider stack context is needed. Google states that Gemini free-tier content may be used to improve its products, so do not treat free-tier Gemini as equivalent to a local/private provider.

The assistant suggests next steps only. It does not apply configuration changes, restart services, or modify files.

The change ledger uses a small SQLite database under `/config/ai-diagnostics`. It stores redacted change metadata, not copied log content. Log scans are performed on demand, and follow-up sessions remain bounded in memory. The feature therefore does not create a second full-log archive or materially multiply normal log storage.

AI Assist does not expose unrestricted shell commands, arbitrary SQL, arbitrary path reads, or config mutation tools to the model. Recommendations are review-only and include risk and restart context when the evidence supports them.
