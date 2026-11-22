# Matched Dell run and OpenRouter pilot

## Dell comparison

Run Pavel V2's 29 synthetic Russian text scenarios on both Gemma 4 E2B Q4_K_M and the exact Qwen3 4B Instruct 2507 Q4_K_M that Pavel used. Start with Gemma, then run Qwen after Gemma unloads. Use GPU-backed Ollama 0.40.13 with a 4,096-token context, a 1,024-token output limit, temperature 0, top-k 40, top-p 0.95, min-p 0 and seeds 42, 43 and 44. Use native non-streaming JSON chat for both models. Disable thinking for Gemma if supported. Qwen3 Instruct 2507 has no thinking variant in this checkpoint. Check GPU placement and report actual model digest, VRAM bytes, active context, case coverage and per-seed scores.

This profile is chosen for the Dell. The earlier checkpoint-matched Qwen run used 16,384 context, a 2,048-token output cap and streaming and remains a separate report row. Pavel's reference was native llama.cpp on Windows. [Existing measurements](pavel-v2-local-ollama.md)

The [native Ollama adapter](../configurations/pavel-v2/adapters/run_ollama_native.py) is copied beside `run_portable.py` in the extracted archive. Set `GEB_MATCHED_PROFILE=1` on both runs and `GEB_OLLAMA_NO_THINK=1` on Gemma only. Invoke it with the same flags as the portable runner and an Ollama loopback `/v1/chat/completions` URL. The adapter sends native JSON to `/api/chat` on the same host and port. Use the per-request `request_options` in the trace as the effective settings, alongside the frozen original reference described in `conditions.json`. The matched Qwen pilot verified tool calls with returned fixture data.

## OpenRouter pilot

For the prepared free smoke launcher, run `python3 openrouter_smoke.py` from the repository root, or double-click `OpenRouter Smoke.command` on macOS. It checks the current catalog for the exact free model and tool support, then runs MAIL-01 and HOME-02 once. With no environment key, Terminal prompts for it without echoing or saving it. Results and a catalog snapshot go into a new ignored `runs/` folder. `python3 openrouter_smoke.py --check` checks only the public catalog, with no credential or inference. There is no paid fallback. The launcher uses default provider routing and does not claim verified thinking control.

Use the GitHub runner's existing OpenAI-compatible client with two synthetic smoke cases. The free Gemma 4 26B A4B endpoint advertises structured tool calling. It is a cloud capability comparison with a different checkpoint. Qwen3.5 9B is a metered candidate and is also a different checkpoint from Pavel's Qwen3 4B. Keep model IDs explicit and record the returned provider and actual request usage when available. The public catalog and free rate limits can change. The November 22 catalog returned zero input and output pricing and tool support for the pinned Gemma endpoint. It did not list the exact Qwen3 4B Instruct 2507 checkpoint. The two-case scripted dry run passed. Live inference requires an OpenRouter key and has not run. [Gemma endpoint](https://openrouter.ai/google/gemma-4-26b-a4b-it:free) · [Qwen endpoint](https://openrouter.ai/qwen/qwen3.5-9b) · [Free limits](https://openrouter.ai/collections/free-models)

The pilot uses synthetic fixtures committed to this repository. It sends no local files, email credentials or device access. Export a dedicated OpenRouter API key through the local shell or secret store, then run from the repository root.

```bash
python3 run_tests.py \
  --base-url https://openrouter.ai/api/v1 \
  --api-key-env OPENROUTER_API_KEY \
  --model google/gemma-4-26b-a4b-it:free \
  --only MAIL-01,HOME-02 \
  --max-tokens 1024 \
  --timeout 120 \
  --output runs/openrouter-gemma4-26b-smoke
```

Review the two traces for real structured tool calls and valid final state before expanding to the text suite. Record rate limits as missing observations. For a paid run, set a dedicated key spending cap and record the provider and price. The key must stay out of GitHub, logs and chat.

## OpenRouter and GPU server sequence

Follow the [combined API and GPU server plan](server-test-plan.md). OpenRouter is the first stage for task comparisons; a rented 48 GB GPU is the second stage for Inkling Q4/Q8 and measured memory/speed. The stages have separate proposed $5 usage limits, pending approval before paid execution.

After the two-case API smoke, run all 16 baseline and all 10 advanced cases once, then add two repeats within budget. Use the same suite commit, grader and request limits as the server comparison; preserve all failures. Keep Pavel's 29-case runner and rubric separate. Record provider routing, actual cost and verified thinking behavior; the current client does not expose provider-pinning controls, and its Qwen thinking option must not be assumed to work identically through OpenRouter. Do not describe an API model as the exact server GGUF without artifact evidence.
