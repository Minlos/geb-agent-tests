# Local model testing to-do list

Test on Philip's Dell G3 3590: i7-9750H, 16 GB RAM, GTX 1660 Ti Max-Q with 6 GB nominal VRAM. The purpose is to compare task completion, unsafe attempts and elapsed time using the same suite. These tasks are planned; no new model run is claimed below.

## Models, in priority order

- [ ] **1. `qwen3:4b-instruct-2507-q4_K_M`** — test the checkpoint named in Pavel's report. It is already non-thinking. This matches the checkpoint, not necessarily Pavel's quantization, runtime or test environment. Published package size: about 2.5 GB. [Ollama tags](https://ollama.com/library/qwen3/tags).
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

- [ ] Keep the checkpoint-matched Qwen3-4B-Instruct-2507 result separate from Qwen3.5:4b.
- [ ] Obtain Pavel's exact quantization, model artifact and runnable test code before describing a run as a reproduction of his results.
- [ ] Compare hardware speed only with matched model/runtime/settings and the same timing metric. Pavel did not report a Gemma run, so our Gemma results are not a direct comparison with his model.
