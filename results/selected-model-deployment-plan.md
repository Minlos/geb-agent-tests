# Hardware and tests for the three selected models

Philip selected Gemma 4 31B Q4, Qwen3.8-27B and Qwen3.6-35B-A3B. The first stage is one unified T01–T36 OpenRouter pilot per checkpoint (42 observations with variants), with a **$1 aggregate limit**. The second stage is an exact-GGUF local deployment check. API and GGUF results must remain separate.

## Exact local artifacts

| Model | Selected weight file | Weight size, decimal GB |
|---|---|---:|
| Gemma 4 31B-it | `lmstudio-community/gemma-4-31B-it-GGUF` / `gemma-4-31B-it-Q4_K_M.gguf` | 18.687 |
| Qwen3.8-27B | `unsloth/Qwen3.8-27B-GGUF` / `Qwen3.8-27B-UD-Q4_K_M.gguf` | 16.564 |
| Qwen3.6-35B-A3B | `unsloth/Qwen3.6-35B-A3B-GGUF` / `Qwen3.6-35B-A3B-UD-Q4_K_M.gguf` | 22.135 |

Repository revisions and SHA-256 hashes are frozen in [the artifact manifest](../configurations/selected-q4-models.json). The Unsloth `UD-Q4_K_M` label is preserved: it is not silently treated as an identical conversion to another publisher's Q4 file. No weights have been downloaded here. Context cache and runtime buffers are additional to file size.

## Hardware shortlist

| Option | What it would establish | Price and current limitation |
|---|---|---|
| FAEX1 / Ryzen AI Max+ 395 / 64 GB shared RAM / 2 TB | Whether all three exact Q4 artifacts run with tools at acceptable latency on the lower-cost shared-memory option | Seller lists **₽235,500**, under order, 10 days. BIOS allocation and compatible Radeon backend require validation. |
| Same platform / 128 GB shared RAM / 2 TB | More room for larger quantizations, context and other processes | Seller lists **₽319,000**, under order, 10 days. More RAM does not by itself make these same Q4 files faster. |
| Desktop with RTX 3090 24 GB | CUDA comparison on the same files | A current complete quote is still missing. Qwen3.6's 22.1 GB file leaves limited overhead on a 24 GB GPU; do not promise full offload or long context without measurement. |
| Rented 48 GB CUDA GPU | Exact Q4 file compatibility and a CUDA quality/speed reference before purchase | Fits the existing [server experiment plan](server-test-plan.md). No rental has been authorized or provisioned in this stage. This does not validate Radeon performance. |

Source for both shared-memory configurations: [seller's complete configuration table](https://www.fevm.store/products/faex1/). Verify final configuration, total price, stock and warranty before payment. The `variant` query on the seller page did not reliably select the displayed configuration, so use the visible configuration table and a written quote. [Full four-tier comparison](hardware-tiers-and-pavel-models.md).

## Local acceptance check

1. Load one model at a time, text only, 4,096 context, one request at a time. Record build, backend, template, actual allocation and any CPU offload.
2. Verify structured tools with MAIL-01 and HOME-02. Configure and verify the checkpoint's thinking control; do not infer it from an unrelated API flag.
3. Run all 36 unified scenarios (42 observations with variants) with the same suite/limits and inspect transcripts. Record actions, final state, unsafe attempts, truncation and latency. Then repeat promising configurations three times.
4. Measure the intended document and voice workload alongside inference before choosing the final machine. No target tokens-per-second or household response-time requirement has yet been agreed or demonstrated on these systems.

Pavel's workbook lists candidates and reasons to test them. It does not specify quantization, hardware or measured scores. These deployment checks supplement that list; they do not demonstrate that the list is wrong. The Gemma 31B API pilot cannot establish how its Q4 GGUF performs locally.
