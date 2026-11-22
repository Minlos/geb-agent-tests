# OpenRouter mail and device smoke checks

The smoke checks test whether OpenRouter can run the synthetic MAIL-01 and HOME-02 scenarios through the existing structured-tool client. One email case completed successfully. The remaining requests were rate-limited, so there is no completed two-case model comparison.

| Model | MAIL-01 | HOME-02 | Evidence |
|---|---|---|---|
| `google/gemma-4-26b-a4b-it:free` | HTTP 429 before an answer | Not attempted after API error | [Raw attempt](raw/openrouter-gemma4-26b-smoke.json) |
| `google/gemma-4-31b-it:free` | HTTP 429 before an answer | Not attempted after API error | [Raw attempt](raw/openrouter-gemma4-31b-smoke.json) |
| `liquid/lfm-3-1.7b:free` | Pass | HTTP 429 | [Raw attempt](raw/openrouter-lfm3-17b-smoke.json) |
| `liquid/lfm-3-1.7b:free`, isolated device retry | Not selected | HTTP 429 | [Raw retry](raw/openrouter-lfm3-home02-retry.json) |

Liquid returned the delivery order number and time using the synthetic mail tools. This verifies a working credential and API/tool loop for that case, not overall model reliability. HTTP 429 rows are missing task observations, not scored task failures. The Gemma 31B and Liquid models were separate free integration probes after the planned Gemma endpoint was throttled.

A bounded diagnostic for the planned Gemma endpoint identified Google AI Studio's shared upstream pool as temporarily rate-limited (`upstream_provider_shared_pool`). The key metadata reported a valid free-tier account with zero recorded usage at that check. No key or account identifier is included in the evidence. Liquid's 429 responses were not diagnosed beyond their HTTP status.

The public catalog listed zero input/output prices and structured tools for the selected endpoints. No paid fallback was used. Runs used suite v0.1.5, temperature 0, 1,024 output tokens, one repeat, a 120-second request timeout, default provider routing and no thinking override. Source hashes, original API messages and returned usage are in the raw files. A separate four-token diagnostic request was not a scored scenario.

Next action: retry the incomplete free smoke checks after upstream availability recovers. Keep these attempts in the record. Expansion to the full suites remains governed by the [combined plan](server-test-plan.md); no full API benchmark has run.

## Gemma retry

A further request to `google/gemma-4-26b-a4b-it:free` again returned HTTP 429 on MAIL-01 before any answer; HOME-02 was not attempted. This adds no scored observation. [Raw retry](raw/openrouter-gemma4-26b-retry.json). A metered two-case fallback with a $0.50 maximum has been proposed and remains pending approval.
