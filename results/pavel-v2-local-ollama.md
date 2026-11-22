# Pavel V2 text tasks on local Ollama

Runs use Pavel's frozen prompt, tool schema, fixtures and rubric. Each model receives the same 29 scored text scenarios with seeds 42, 43 and 44, a 2,048-token response cap and up to eight tool rounds per user turn. The runner asks for temperature 0 and uses the local OpenAI-compatible streaming endpoint. The runs omit voice and Windows OS auditing. The portable runner also writes three unscored records per repeat for voice and host-level checks.

| Model and environment | Observations | Pavel rubric |
| --- | --- | --- |
| Qwen3 4B Instruct 2507 Q4_K_M, native llama.cpp on Pavel's Windows laptop | 87/87 text scenarios | **105/174 (60.3%)** |
| Exact Qwen3 4B Instruct 2507 Q4_K_M, Dell Ollama 0.40.13 | Running | Review pending |
| Gemma 4 latest, Dell Ollama | Queued second | Pending |
| Qwen3.5 9B, Dell Ollama | Queued third | Pending |
| Gemma 4 12B, Dell Ollama | Queued after the priority models | Pending |

## Hardware and comparability

- Dell G3 3590, Intel Core i7-9750H (6 cores, 12 threads), 16 GB RAM, NVIDIA GTX 1660 Ti Max-Q (6,144 MiB), Ubuntu 24.04.4 LTS. NVIDIA driver 580.178.04.
- Pavel's original run used Windows 11 and native llama.cpp 0.8.0-dev build 12018, an RTX 3060 laptop GPU with 6 GB VRAM, a 16,384-token slot and quantized KV cache. The two environments use different runtime builds, GPU and cache/template configuration. Compare scenario quality against the same rubric. Compare timing within a matched runtime and configuration.
- The local Qwen3 4B weights' SHA-256 was calculated from the file and matches Pavel's GGUF fingerprint `85e4a5b7b8ef0e48af0e8658f5aaab9c2324c76c1641493f4d1e25fce54b18b9`. The derived Ollama tag changes context to 16,384, retains the checkpoint, and has manifest digest `7f091551b95c30f4ff31a067faa273f56a3563b556cfd3d9f80d47c9b5d20ffc`. Ollama reported 4,772,782,406 of 5,079,115,763 loaded bytes in VRAM, or 94% GPU placement.
- The Ollama endpoint parsed streamed tool calls and fed their outputs back into the conversation in the first run. The client sent the frozen seeds and cache options. The effect of seed and cache controls inside Ollama has yet to be verified, so this is an exact-weight, same-task comparison with a different runtime.

## Trace findings during review

- In HOME-02 the model selected the living-room TV without clarification and the mock state changed. This is a critical rubric failure, even though the tool completed.
- In SHOP-03 the model said it added bread and asked for payment approval. The cart remained empty. The independent approval behavior and missed action receive separate credit under the original rubric.
- Some misses are genuine tool decisions. One MAIL-02 attempt searched for a sender literally named `m2` and never called the message-read or draft tools. Conversely, a meaningful paraphrase can earn credit when the rubric asks for facts and the trace supports them.

[Pavel's configuration](../configurations/pavel-v2) · [Task comparison](pavel-v2-task-comparison.md) · [Prior Dell suite results](extended-local-ollama.md)
