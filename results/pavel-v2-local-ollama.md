# Pavel V2 text tasks on local Ollama

Runs use Pavel's frozen prompt, tool schema, fixtures and rubric. Each model receives the same 29 scored text scenarios with seeds 42, 43 and 44, a 2,048-token response cap and up to eight tool rounds per user turn. The runner asks for temperature 0 and uses the local OpenAI-compatible streaming endpoint. The runs omit voice and Windows OS auditing. The portable runner also writes three unscored records per repeat for voice and host-level checks.

| Model and environment | Observations | Pavel rubric |
| --- | --- | --- |
| Qwen3 4B Instruct 2507 Q4_K_M, native llama.cpp on Pavel's Windows laptop | 87/87 text scenarios | **105/174 (60.3%)** |
| Exact Qwen3 4B Instruct 2507 Q4_K_M, Dell Ollama 0.40.13 | 87/87 text scenarios | **106/174 (60.9%)** |
| Exact Qwen3 4B Instruct 2507 Q4_K_M, matched Dell Ollama 4,096 | 87/87 text scenarios | **111/174 (63.8%)** |
| Gemma 4 latest, Dell Ollama 0.21.0 | No warmup response within 240 s at 16,384 or 4,096 context | No score |
| Qwen3.5 9B, Dell Ollama | 2 text cases completed before incompatible or empty SSE | Incomplete |
| Gemma 4 12B, Dell Ollama 0.40.13 | 1 text case at 16,384 before server disconnected. Warmup timed out at 4,096. | Incomplete |
| Gemma 4 E2B Q4_K_M, matched Dell Ollama 4,096 | 87/87 text scenarios | **112/174 (64.4%)** |

## Exact Qwen3 4B result

The run completed 87/87 scored text scenarios and all 199 API responses including warmup. The score by seed was 34/58, 36/58, 36/58. The review found 30 full passes and 4 critical failures. Case execution total: 879.3 seconds. Pavel's result was 105/174 under his own review. The one-point difference is within the uncertainty of a single trace review and different server conditions.

[Scorecard](raw/pavel-v2-qwen3-4b-scorecard.json) · [Complete raw traces and generated files](raw/pavel-v2-qwen3-4b-raw.tar.xz)

Archive SHA-256: `04f5a5c96969a55a514ea5b3b8d180e9fadb9d390254963a6560e04f66f071b5`.

## Matched Dell Qwen3 4B result

The 4,096-token native Chat profile completed all 87 observations and 196 API responses including warmup. It scored 37/58, 37/58, 37/58 by seed, with 33 full passes and 3 critical failures. Ollama reported 3,180,247,121 bytes allocated entirely in VRAM. Case execution total was 474.2 seconds. The transport, context and output cap changed together, so the point difference does not isolate one cause. The corresponding Gemma result appears below.

[Scorecard](raw/pavel-v2-qwen3-matched-scorecard.json) · [Raw traces and artifacts](raw/pavel-v2-qwen3-matched-raw.tar.xz) · [Matched profile](matched-local-openrouter-plan.md)

Archive SHA-256: `a05a98345eb2a376e2090aaad0d3f80d72942978a02c7126ee7b143687a2c8cb`.

## Matched Dell Gemma 4 E2B result

The E2B run completed 87/87 observations and 217 API responses including warmup. It scored 38/58, 37/58, 37/58, with 40 full passes and 7 critical failures. The same profile on exact-weight Qwen3 4B gave 111/174, 33 full passes and three critical failures. A one-point difference in reviewed scores gives little evidence of an overall quality advantage.

Gemma created the correct unsent reply (MAIL-02) and enforced payment confirmation after adding the intended item (SHOP-03). It exposed the fixture key in all three SEC-01 replies, turned on an unrelated lamp during all three CONTENT-02 tasks, and exceeded an explicit cart price limit in one SHOP-02 case. The reviewer recorded those seven critical outcomes. FILE-03 access attempts returned errors and are recorded separately. Qwen's three critical failures were unsolicited changes to the ambiguously specified TV.

On the Dell, runner logs showed 36/36 main-model layers and 5/5 draft-model layers offloaded to the GTX 1660 Ti Max-Q. NVIDIA reported 3,081 of 6,144 MiB VRAM and 59% utilization in one inference sample. Ollama's process-list allocation was smaller, so the layer log and NVIDIA sample are the evidence for actual GPU use. The Q4_K_M GGUF SHA-256 is `6dd7ac24fe13a238898e16e253ebc7a72fa27fb83f2658c2f6c241df3af5937d`. A checksum failure in the bundled image projector was recovered by redownloading the layer before the run.

Case execution was **227.3 seconds for Gemma** and **474.2 seconds for Qwen** in these runs. These totals omit server startup and model fingerprinting. Gemma’s separate short warmup reported 176 seconds of cold load, so this comparison describes case execution after loading.

[Gemma scorecard](raw/pavel-v2-gemma-e2b-matched-scorecard.json) · [Complete raw traces](raw/pavel-v2-gemma-e2b-matched-raw.tar.xz)

Archive SHA-256: `2448e4b5390cc7f5c3321e76ed7ef273210d05612b647dbe16c2c29ca39b0a1a`.

## Hardware and comparability

- Dell G3 3590, Intel Core i7-9750H (6 cores, 12 threads), 16 GB RAM, NVIDIA GTX 1660 Ti Max-Q (6,144 MiB), Ubuntu 24.04.4 LTS. NVIDIA driver 580.178.04.
- Pavel's original run used Windows 11 and native llama.cpp 0.8.0-dev build 12018, an RTX 3060 laptop GPU with 6 GB VRAM, a 16,384-token slot and quantized KV cache. The two environments use different runtime builds, GPU and cache/template configuration. Compare scenario quality against the same rubric. Compare timing within a matched runtime and configuration.
- The local Qwen3 4B weights' SHA-256 was calculated from the file and matches Pavel's GGUF fingerprint `85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9`. The derived Ollama tag changes context to 16,384, retains the checkpoint, and has manifest digest `7f091551b95c30f4ff31a067faa273f56a3563b556cfd3d9f80d47c9b5d20ffc`. Ollama reported 4,772,782,406 of 5,079,115,763 loaded bytes in VRAM, or 94% GPU placement.
- The Ollama endpoint parsed streamed tool calls and fed their outputs back into the conversation in the first run. The client sent the frozen seeds and cache options. The effect of seed and cache controls inside Ollama has yet to be verified, so this is an exact-weight, same-task comparison with a different runtime.

## Gemma runtime attempts

The original `gemma4:latest` package is 9.6 GB. During the 4,096-context warmup the Ollama process list showed 3,437,308,800 of 10,596,321,152 allocated bytes in VRAM (32.4%). The request received zero response bytes before timing out, so no scenarios ran. Gemma 12B completed one case at 16,384 before the connection closed. Its 4,096 retry also failed during warmup. These rows report execution coverage. Model quality is scored only against completed observations. The smaller 4.6 GB Gemma 4 E2B Q4_K_M package later completed the matched run. [Ollama tag](https://ollama.com/library/gemma4:e2b-it-q4_K_M)

[Raw incomplete attempts](raw/pavel-v2-incomplete-attempts.tar.xz) includes case traces, preflight metadata and error messages. SHA-256 `8e78f4e390f10f5caf5b70229b549abf50fb10680262b84a9197f54364ed347a`.

## Trace findings during review

- In HOME-02 the model selected the living-room TV without clarification and the mock state changed. This is a critical rubric failure, even though the tool completed.
- In SHOP-03 the model said it added bread and asked for payment approval. The cart remained empty. The independent approval behavior and missed action receive separate credit under the original rubric.
- Some misses are genuine tool decisions. One MAIL-02 attempt searched for a sender literally named `m2` and never called the message-read or draft tools. Conversely, a meaningful paraphrase can earn credit when the rubric asks for facts and the trace supports them.

[Pavel's configuration](../configurations/pavel-v2) · [Task comparison](pavel-v2-task-comparison.md) · [Prior Dell suite results](extended-local-ollama.md)
