# Local model testing to-do list

Test on Philip's Dell G3 3590: i7-9750H, 16 GB RAM, GTX 1660 Ti Max-Q with 6 GB nominal VRAM. The purpose is to compare task completion, unsafe attempts and elapsed time using the same suite. Completed runs are published in the [extended benchmark report](results/extended-local-ollama.md).

## Models, in priority order

- [x] **1. `qwen3:4b-instruct-2507-q4_K_M`** — test the checkpoint named in Pavel's report. It is already non-thinking. This matches the checkpoint, not necessarily Pavel's quantization, runtime or test environment. Published package size: about 2.5 GB. [Ollama tags](https://ollama.com/library/qwen3/tags).
- [ ] **2. `phi4-mini:3.8b`** — compare a different compact model family with function calling and documented Russian support. Published package size: about 2.5 GB. [Ollama model](https://ollama.com/library/phi4-mini) · [Microsoft model card](https://huggingface.co/microsoft/Phi-4-mini-instruct).
- [ ] **3. `qwen3.5:9b`** — test whether a larger Qwen improves reliability over the tested 4B. Use thinking disabled on a compatible endpoint and record that setting. Its published 6.6–7.6 GB package exceeds the GPU's nominal memory; expect CPU offloading. [Ollama model](https://ollama.com/library/qwen3.5).
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

## Pavel comparison

- [x] Keep the checkpoint-matched Qwen3-4B-Instruct-2507 result separate from Qwen3.5:4b.
- [ ] When Pavel shares his conditions, record the exact model artifact/digest and quantization; llama.cpp build; Open WebUI version; chat template and system prompt; context, sampling, thinking and output limits; GPU layers; laptop CPU/RAM and GPU power setting. The two Qwen models currently reported are different checkpoints, despite both having 4B parameters.
- [ ] Obtain Pavel's runnable cases, fixtures, tool schemas, expected outcomes, grading rules and raw transcripts. Confirm whether each reported action used an actual tool or was only described in a reply. Store only synthetic data or material approved for public sharing.
- [ ] Run Qwen3-4B-Instruct-2507 and Qwen3.5:4b on our same suite and Dell with matched settings where supported. Record checkpoint-specific template and thinking differences. Use the procedure above, including three repeats and transcript review.
- [ ] Once Pavel's runnable suite is available, run it as a separate suite and preserve its scoring. If the same checkpoint still differs between setups, compare runtime/template, context and generation settings one at a time. A reproduction requires matching the model artifact and test conditions.
- [ ] Compare hardware speed only with matched model/runtime/settings and the same timing metric. Pavel did not report a Gemma run, so our Gemma results are not a direct comparison with his model.

## Inkling-2-Mini-Unbound: conditional candidate

Pavel forwarded [nokeepai/Inkling-2-Mini-Unbound-GGUF](https://huggingface.co/nokeepai/Inkling-2-Mini-Unbound-GGUF). Assess it after the compact models above. The publisher lists Q4_K_M weights at 17.6 GB and BF16 at 52.2 GB. These sizes exclude runtime memory. On the Dell's 16 GB RAM and 6 GB VRAM, Q4 would require substantial CPU/GPU splitting and a measured memory check; practical speed and sufficient available memory are not established. Starting with BF16 is not a useful Dell test plan.

- [ ] Verify the installed runtime supports `inkling2_loop`, the required loop fix (publisher references llama.cpp PR #32704), the supplied chat template and structured tool calls. Confirm MAIL-01 and HOME-02 work before allocating a full benchmark run. GGUF format alone does not establish runtime compatibility.
- [ ] Choose hardware, quantization and context from measured available memory. Record peak RAM/VRAM, swapping, time to first token and generation speed in a short trial. If Q4 cannot run usefully on the Dell, defer to suitable hardware or an API serving this exact model.
- [ ] If comparing quantizations, keep the checkpoint, runtime, context, prompts and generation settings fixed. Score task completion and unsafe attempts as well as speed; report allocation errors and timeouts separately. Lower bit counts are a memory tradeoff, not evidence of adequate quality.
- [ ] If feasible, compare Unbound with the original Inkling-2-Mini at matching quantization and settings. The publisher's reduced-refusal results do not establish better mail/file tool use; its card says agent benchmarks have not been run. Include our injection, secret-access and send-confirmation cases in the comparison.
- [ ] Record Inkling's actual thinking behavior and endpoint controls rather than assuming our Qwen `--no-thinking` option maps identically. The publisher says effort 0 can still produce brief thinking.

Compatibility requirements and file sizes above are publisher statements from the linked model card, not a verified local installation or benchmark.

## GPU server experiment

- [x] Prepare a [bounded server test plan](results/server-test-plan.md): one 48 GB GPU, Inkling Q4 versus Q8, Qwen3.5:4b comparison, 16 baseline plus 10 advanced cases, and up to three repeats.
- [ ] Agree the provider and proposed $5 total usage / four-hour limit before provisioning. Recheck the live rental and storage price.
- [ ] Execute the plan, publish raw evidence and comparison, then terminate the instance and check retained storage charges.
