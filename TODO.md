# Local model testing to-do list

## Advanced-1.0

- [x] Implement 32 scenarios from Grok ideas with explicit fixtures, dialogue, independent permissions, grading and offline checks. [Instructions](docs/advanced-32.md).
- [ ] Run frozen original/v3 on the new suite when authorized; retain every attempt and manually review critical flags and paired differences. No model run is included in implementation readiness.

## Hardware budget and current API status

[Selected-model deployment plan](results/selected-model-deployment-plan.md) · [Pinned exact GGUF artifacts](configurations/selected-q4-models.json)

- [x] Compare [four budget tiers and all six Pavel spreadsheet candidates](results/hardware-tiers-and-pavel-models.md), with [CSV comparison](results/pavel-models-by-budget.csv) and [Russian retail research](results/russian-hardware-gemma.md).
- [x] Run paid Gemma 4 31B MAIL-01 and HOME-02 smoke checks: both passed; [evidence and API cost](results/openrouter-smoke.md).
- [x] Execute the approved unified T01–T36 API pilots for Gemma 31B, Qwen3.8-27B and Qwen3.6-35B-A3B within $1 total, carrying forward earlier spend/reservations. [Results](results/unified-openrouter-pilot.md): Gemma and Qwen3.8 completed all conversations; Qwen3.6 has one unfinished scenario. API scores are not exact GGUF Q4 measurements.
- [x] Record [ADR 0001: specialize smaller models for narrow household tasks](docs/adr/0001-specialized-small-models.md). Training has not started; define an experiment and a new unseen holdout before evaluating adoption.
- [ ] Before hardware purchase, obtain the final complete quote and benchmark the exact local artifact and runtime. Gemma 31B Q4 has much lower memory needs than BF16; local quality and latency remain to be measured.

Publish each completed project deliverable on GitHub as soon as it is ready. Link the report, raw traces and runtime metadata where applicable. Label incomplete runs and record their coverage separately.

Test on Philip's Dell G3 3590: i7-9750H, 16 GB RAM, GTX 1660 Ti Max-Q with 6 GB nominal VRAM. The purpose is to compare task completion, unsafe attempts and elapsed time using the same suite. Completed runs are published in the [extended benchmark report](results/extended-local-ollama.md).

## Historical small-model plan

The 16+10 procedure below is retained for historical comparisons. The current selected-model runs use the unified36 implementation in the README.

## Models, in priority order

- [x] **1. `qwen3:4b-instruct-2507-q4_K_M`** — test the checkpoint named in Pavel's report. It is already non-thinking. Pavel's GGUF SHA-256 matches the local weights byte for byte. Runtime and hardware differ. Published package size: about 2.5 GB. [Ollama tags](https://ollama.com/library/qwen3/tags).
- [ ] **2. `phi4-mini:3.8b`** — compare a different compact model family with function calling and documented Russian support. Published package size: about 2.5 GB. [Ollama model](https://ollama.com/library/phi4-mini) · [Microsoft model card](https://huggingface.co/microsoft/Phi-4-mini-instruct).
- [x] **3. `qwen3.5:9b`** — test whether a larger Qwen improves reliability over the tested 4B. Use thinking disabled on a compatible endpoint and record that setting. Its published 6.6–7.6 GB package exceeds the GPU's nominal memory; expect CPU offloading. [Ollama model](https://ollama.com/library/qwen3.5).
- [ ] **4. `ministral-3:8b`** — test whether the larger model addresses the observed 3B failures. Its approximately 6 GB package leaves no room for runtime overhead within 6 GB VRAM; expect some CPU offloading. [Ollama tags](https://ollama.com/library/ministral-3/tags).

Package sizes are not total runtime memory. Verify current tags and record the actual downloaded model digest and quantization. Run one model at a time.

## Procedure for each model

- [ ] Record model digest/quantization, Ollama or other runtime version, endpoint, actual context allocation, thinking setting, output limit and GPU/CPU placement. Avoid relying on `latest` alone.
- [ ] Confirm structured tool calling with MAIL-01 and HOME-02 before the full run. Investigate API/template errors separately from model failures.
- [ ] Run all **16 baseline cases** and all **10 advanced cases**, in separate result files, with the same prompts, tool schemas, limits and scoring version. Keep the original five-case advanced results separate.
- [ ] Use three repeats per suite for the final comparison, preserving all attempts. Do not combine different thinking modes into one score.
- [ ] Review transcripts for incorrect actions and false claims of completion, including apparent passes. Record blocked unsafe attempts even when the simulator prevented any state change.
- [ ] Publish raw JSON and a results table with full-pass counts, per-repeat results, unsafe attempts, final-answer/format errors and elapsed time. Include the selected case IDs and source hash.
- [ ] Compare with our Qwen3.5:4b thinking-disabled and Gemma runs on the same case set and grader. A failed case remains part of the result; completing this task does not require every model to pass every test.

Use the [runner instructions](README.md), [fix and rerun instructions](results/fix-and-rerun-instructions.md) and [extended test instructions](results/extended-test-instructions.md). Do not send unsupported thinking parameters to models that have no thinking control.

## Pavel comparison and unified benchmark

1. [x] Publish [Pavel's verified bundle](configurations/pavel-v2) as a reproducibility configuration. All 743 checksums and 24 offline checks passed. The local Qwen3 4B Instruct 2507 GGUF has the same SHA-256 as Pavel's.
2. [x] Publish the [crosswalk](results/pavel-v2-task-comparison.md) between both task lists and document differences in fixtures, simulator state, side-effect handling and grading.
3. [x] Publish the [priority model comparison on Pavel's 29 scenarios](results/pavel-v2-local-ollama.md). Both exact Qwen3 4B and Gemma 4 E2B completed the matched GPU profile. Gemma latest, 12B and Qwen3.5 9B have incomplete attempts with raw evidence.
4. [x] Publish the [unified Russian text benchmark proposal](results/unified-text-benchmark-ru.md) based on the two source suites and the matched model results. One runner, 36 scenarios, one scoring scheme and no audio.

## Inkling-2-Mini-Unbound: conditional candidate

Pavel forwarded [nokeepai/Inkling-2-Mini-Unbound-GGUF](https://huggingface.co/nokeepai/Inkling-2-Mini-Unbound-GGUF). Assess it after the compact models above. The publisher lists Q4_K_M weights at 17.6 GB and BF16 at 52.2 GB. These sizes exclude runtime memory. On the Dell's 16 GB RAM and 6 GB VRAM, Q4 would require substantial CPU/GPU splitting and a measured memory check; practical speed and sufficient available memory are not established. Starting with BF16 is not a useful Dell test plan.

- [ ] Verify the installed runtime supports `inkling2_loop`, the required loop fix (publisher references llama.cpp PR #32704), the supplied chat template and structured tool calls. Confirm MAIL-01 and HOME-02 work before allocating a full benchmark run. GGUF format alone does not establish runtime compatibility.
- [ ] Choose hardware, quantization and context from measured available memory. Record peak RAM/VRAM, swapping, time to first token and generation speed in a short trial. If Q4 cannot run usefully on the Dell, defer to suitable hardware or an API serving this exact model.
- [ ] If comparing quantizations, keep the checkpoint, runtime, context, prompts and generation settings fixed. Score task completion and unsafe attempts as well as speed; report allocation errors and timeouts separately. Lower bit counts are a memory tradeoff, not evidence of adequate quality.
- [ ] If feasible, compare Unbound with the original Inkling-2-Mini at matching quantization and settings. The publisher's reduced-refusal results do not establish better mail/file tool use; its card says agent benchmarks have not been run. Include our injection, secret-access and send-confirmation cases in the comparison.
- [ ] Record Inkling's actual thinking behavior and endpoint controls rather than assuming our Qwen `--no-thinking` option maps identically. The publisher says effort 0 can still produce brief thinking.

Compatibility requirements and file sizes above are publisher statements from the linked model card, not a verified local installation or benchmark.

## OpenRouter and GPU server experiments

- [x] Prepare the [combined plan](results/server-test-plan.md): OpenRouter task comparison first, then one 48 GB GPU for Inkling Q4 versus Q8 and a Qwen3.5:4b comparison. Both use 16 baseline plus 10 advanced cases, with up to three repeats.
- [ ] Complete the OpenRouter smoke, then the full suites. Start with the free endpoint in the [API pilot](results/matched-local-openrouter-plan.md); agree a separate $5 API usage cap before metered inference. Verify provider routing and thinking controls, and record costs.
- [ ] Agree the provider and proposed $5 total usage / four-hour limit before provisioning. Recheck the live rental and storage price.
- [ ] Execute the plan, publish raw evidence and comparison, then terminate the instance and check retained storage charges.

## Matched Dell and OpenRouter runs

- [x] Run [the matched Dell profile](results/matched-local-openrouter-plan.md) on Gemma 4 E2B and exact-checkpoint Qwen3 4B, with Gemma first and one GPU model loaded at a time.
- [ ] Start the free OpenRouter smoke test as soon as an API key is available, then follow the full API stage above. Compare API and GPU-server results on the same cases, preserving separate provider/runtime and hardware details.

## Research after the core comparison and unified proposal

- [x] Survey [related benchmarks](results/related-benchmarks.md) and document [coverage gaps for Russian-speaking users](results/pavel-v2-benchmark-gaps-ru.md). The proposed benchmark uses Russian text, a single runner and a single scoring scheme.
- [x] Publish the [integrated GEB test report](results/geb-test-report.md) covering both source suites, measured results and external evaluation methods.
