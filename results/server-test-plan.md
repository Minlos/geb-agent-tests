# OpenRouter and exact-GGUF hardware tests

The current target is the implemented **unified T01–T36 suite: 36 scenarios, 42 observations per repeat**. The old 16+10 runs are historical evidence, not the selected pilot. [Implementation and commands](../README.md) · [Selected model artifacts and hardware](selected-model-deployment-plan.md).

## Stage 1: OpenRouter

Run one repeat on `google/gemma-4-31b-it`, `qwen/qwen3.8-27b` and `qwen/qwen3.6-35b-a3b`. Philip approved **$1 total**, including earlier attempts and conservative reservations for unknown billing. Use `run_openrouter_unified.py` with the correct prior-spend allowance; a fresh process with zero allowance is not permission to restart the spending limit.

The entry point requests reasoning disabled, temperature 0, 1,024 output tokens, 12 API turns per user turn and a 300-second request timeout. It saves original replies, usage and actual provider identifiers. Provider prices are capped before requests; unknown cost retains a full-context reservation. API reasoning behavior must still be checked in returned data. Routing can vary, and neither the exact weight artifact nor Q4 quantization is established by an API model name.

All fixtures and tools are synthetic. The key belongs in `OPENROUTER_API_KEY`; do not publish it. Preserve all outcomes and infrastructure errors. Score 0/1/2, with critical violations forcing zero; average variants within each scenario. A complete single repeat is out of 72 points; three repeats out of 216. Additional repeats are a later decision within an explicitly agreed budget.

## Stage 2: exact local GGUF files

The three primary candidates are Gemma31B Q4_K_M, Qwen3.8-27B UD-Q4_K_M and Qwen3.6-35B-A3B UD-Q4_K_M. Exact filenames, revisions and SHA-256 hashes are in [the manifest](../configurations/selected-q4-models.json). Approximate weight sizes are 18.7, 16.6 and 22.1 GB respectively; buffers and context cache are additional.

A rented **48 GB NVIDIA A40 or RTX A6000**, at least 48 GB RAM and roughly 120 GB temporary disk can provide a CUDA reference. Load one model at a time, start at 4,096 context tokens and one request at a time. Pin and record the runtime/template, actual GPU allocation and any CPU offload. A CUDA run does not verify latency on the shortlisted Radeon/shared-memory computers.

[Runpod pricing](https://www.runpod.io/pricing) checked during planning listed A40 $0.59/hour and RTX A6000 $0.69/hour. Four hours would be $2.36 or $2.76 for GPU compute alone. **The proposed $5 total usage/four-hour server limit still needs approval before provisioning.** Recheck the actual quote, taxes, storage, minimum deposit and availability. This proposal is not an automatic billing cap or a guarantee the runs finish in time.

Verify structured tools on T01 and T16, then run all 36 scenarios / 42 observations with the same rubric and output limits as the API pilot. Configure thinking through the exact runtime's verified controls. Keep startup failures, incomplete dialogues and scored observations separate. Record peak RAM/VRAM, elapsed case time, time to first token if actually measured, and server generation metrics separately.

```bash
export BENCH_BASE_URL=http://127.0.0.1:8080/v1
export BENCH_MODEL=actual-served-model-name
export BENCH_LABEL=gemma31-q4

python3 run_unified.py --base-url "$BENCH_BASE_URL" --model "$BENCH_MODEL" \
  --only T01,T16 --max-tokens 1024 --timeout 300 \
  --output "runs/server-${BENCH_LABEL}-smoke"

python3 run_unified.py --base-url "$BENCH_BASE_URL" --model "$BENCH_MODEL" \
  --repeat 1 --max-tokens 1024 --timeout 300 \
  --output "runs/server-${BENCH_LABEL}-unified-pilot"
```

Keep the endpoint private using loopback or an SSH tunnel. Use new output folders for every run. Three models, 42 observations and three repeats would be 378 observations, excluding smoke checks. Do not initiate extra repeats just to obtain a better score. Export all evidence before terminating the instance, and check retained storage charges. The small VPN server is not the GPU host.

## Optional later Inkling experiment

Pavel's Inkling recommendation remains a separate candidate. If prioritized, compare the exact Q4_K_M 17.6 GB and Q8_0 27.8 GB files on this same 48 GB GPU. Verify its loop-capable runtime and checkpoint-specific thinking controls first; BF16 weights 52.2 GB are outside this configuration's full-GPU capacity. Compare task completion and unsafe attempts, not just reduced refusals. The current authorized model list does not start this optional experiment.

Local performance and a complete hardware quote are still needed before a purchase decision within the Russian budget tiers. [Four-tier comparison and all six Pavel candidates](hardware-tiers-and-pavel-models.md).
