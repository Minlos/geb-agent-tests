# Four computer budgets and Pavel's model shortlist

The aim is to choose a complete local computer and models for GEB, with budget ceilings of ₽100,000, ₽200,000, ₽300,000 and ₽400,000–500,000. Prices were checked on 22 November 2026. These are seller listings, not confirmed quotes. Model fit below is a memory assessment for one loaded model and an initial 4,096-token context, not a measured speed or test score.

## Hardware at each budget

| Budget ceiling | Configuration to investigate | Public listing and qualification |
|---|---|---|
| ₽100,000 | RTX 3060 **12 GB**, 32 GB system RAM, 1 TB SSD | [ITB: Ryzen 5 5500X3D / RTX 3060 / 32 GB / 1 TB](https://balakovo.it/computers/moshchnyi-igrovoi-r5-5500-x3d-rtx-3060-12gb-32gb): ₽89,990, **under order**, 12-month stated warranty. This is a complete listed PC, not confirmed immediately available stock. |
| ₽200,000 | RTX 5060 Ti **16 GB**, target 32–64 GB system RAM, 1 TB SSD | [КВАНТ configuration](https://quantcomputers.ru/product/5600-16-1000-5060ti16gb-whh/): ₽162,667 with **16 GB system RAM**, ₽152,933 cash. Obtain an upgrade quote within the ceiling. Its title and description disagree about the GPU; require a final exact parts list. |
| ₽300,000 | Ryzen AI Max+ 395, Radeon 8060S, **64 GB shared RAM**, 2 TB SSD | [FEVM FAEX1 configurations](https://www.fevm.store/products/faex1/): ₽235,500 for this configuration. The 128 GB version without SSD is ₽299,000 and is not a complete usable storage configuration within this ceiling. |
| ₽400,000–500,000 | Same processor, **128 GB shared RAM**, 2 TB SSD | [FEVM 128 GB / 2 TB configuration](https://www.fevm.store/products/faex1/?variant=1082): ₽319,000. It already fits below ₽400,000; there is no need to spend the whole ceiling. Check delivered configuration, software support and latency before purchase. |

The 64/128 GB mini PCs share memory between CPU and GPU; this is not 64/128 GB of discrete VRAM. AMD describes up to 96 GB graphics allocation on a 128 GB system, but the actual BIOS, operating system and backend must support the chosen allocation. [AMD memory explanation](https://www.amd.com/en/blogs/2025/experience-unparalleled-performance-with-the-amd-ryzen.html). The RAM is not a later desktop-style upgrade, so choose the memory version before buying. Source pages disagree between in-stock and under-order variants; confirm stock and delivery rather than relying on a badge.

All prices exclude any unlisted delivery, installation, microphones, home-device controllers and support. Seller identity, fulfillment and warranty service have not been independently audited. The lower-price PC listings are leads for a quote, not vetted purchases. A same-price faster gaming GPU with less memory is not automatically a better LLM choice.

## All six models in Pavel's spreadsheet

Source: `geb-v2-models.xlsx`, sheet `Модели V2`, rows 5–10. Pavel's order is preserved. Columns D (score) and E (comments) are empty: the workbook is a **candidate list, not benchmark evidence**.

| Pavel's order and model | Inspected weights, approximately | ₽100k / 12 GB GPU | ₽200k / 16 GB GPU | ₽300k / 64 GB shared | ₽400–500k / 128 GB shared |
|---|---|---|---|---|---|
| 1. Nemotron 3.5 Super VL 120B-A12B | NVFP4 GGUF **76.92 GB**; Q8 **128.47 GB** before additional components | No practical full-GPU fit | No practical full-GPU fit | Not a practical memory target | **Conditional memory candidate at NVFP4**, not Q8. AMD/backend support, any correction/projector files and latency need verification. |
| 2. Qwen3.8-27B | UD-Q4_K_M **16.56 GB**; Q8 **29.05 GB** | Offloading required | Too tight to plan around full GPU loading | **Q4/Q8 candidate** | **Q4/Q8 candidate**, more context headroom |
| 3. gpt-oss-120b | MXFP4 GGUF **63.39 GB** | Offloading required; unsuitable target | Offloading required; unsuitable target | Too tight to recommend after OS/cache/buffers | **Conditional MXFP4 candidate**; verify AMD backend and native tool/reasoning format |
| 4. Qwen3.5-122B-A10B | Q4_K_M shards total **76.54 GB**; MXFP4_MOE about **74.66 GB** | No practical full-GPU fit | No practical full-GPU fit | Not a practical memory target | **Conditional Q4 candidate** with short initial context; runtime and latency unmeasured |
| 5. Gemma 4 31B-it | Q4_K_M **18.69 GB**; Q8 about **32.64 GB** | Offloading required | Offloading required | **Q4/Q8 candidate** | **Q4/Q8 candidate**, more context headroom |
| 6. Qwen3.6-35B-A3B | UD-Q4_K_M **22.13 GB**; Q8 **36.90 GB** | Offloading required | Offloading required | **Q4/Q8 candidate** | **Q4/Q8 candidate**, more context headroom |

All sizes are decimal GB from inspected repository file listings. Split-file totals include every weight shard. The 122B Q4 total is rounded from the combined shard sizes. Context cache, compute buffers, vision projectors and optional speculative draft models are additional. Models with few active parameters still need their total weights in memory; A3B/A10B/A12B is not the storage size.

Weight sources: [Nemotron GGUF](https://huggingface.co/ggml-org/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-GGUF), [Qwen3.8 GGUF](https://huggingface.co/unsloth/Qwen3.8-27B-GGUF), [gpt-oss GGUF](https://huggingface.co/ggml-org/gpt-oss-120b-GGUF), [Qwen3.5 122B GGUF](https://huggingface.co/unsloth/Qwen3.5-122B-A10B-GGUF), [Gemma 31B GGUF](https://huggingface.co/lmstudio-community/gemma-4-31B-it-GGUF), [Qwen3.6 GGUF](https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF).

The three large models are experiments enabled by memory capacity, not guaranteed responsive household assistants. NVIDIA's serving instructions for Nemotron do not establish that its NVFP4 file works efficiently on Radeon. Test the exact backend before buying hardware for that model. CPU offloading may allow additional models to start on cheaper computers; it does not establish useful speed.

## Other models worth considering at each tier

This covers the practical model families relevant to our task, plus all six Pavel candidates above. It is not an exhaustive list of every checkpoint, fine-tune or quantization on Hugging Face. Each entry still needs a structured-tool smoke test; fitting in memory does not establish Russian task quality or a working tool template.

| Earliest tier to investigate | Additional candidates | Starting format and limits |
|---|---|---|
| ₽100k / 12 GB GPU | Gemma 4 E2B, E4B and **12B**; Qwen3.5 0.8B, 2B, 4B, **9B**; Qwen3 0.6B, 1.7B, 4B Instruct 2507, 8B, **14B**; Ministral 3 3B, 8B, **14B**; Phi-4 Mini 3.8B, Phi-4 14B; Llama 3.2 1B/3B and Llama 3.1 8B; our Granite 4 3B comparator | Q4 initially. 12–14B is the upper practical starting group; check cache/buffer allocation. Some models have limited official Russian support or no verified native tools. Smaller variants can use higher precision if memory permits. |
| ₽200k / 16 GB GPU | All preceding models, with more room for Gemma 12B Q6/Q8; **gpt-oss-20b** as a tight-fit experiment | gpt-oss's packaged low-bit weights are about 14 GB, leaving limited runtime headroom; preserve its supported quantization and reasoning format. This tier still does not comfortably fit Pavel's Q4 27–35B group entirely on GPU. |
| ₽300k / 64 GB shared | All preceding models; **Gemma 4 26B-A4B**; Qwen3.5 27B and 35B-A3B; Qwen3 30B-A3B and 32B; **Inkling-2-Mini-Unbound**; Pavel's Qwen3.8, Gemma 31B and Qwen3.6 | Q4–Q8 where total memory permits. Start with 4K context. Inkling requires its loop-capable runtime. This tier provides capacity, not a promised speed improvement over a discrete GPU. |
| ₽400–500k / 128 GB shared | All preceding models; **Llama 3.3 70B Q4**; the three large Pavel candidates as separately qualified experiments | Use measured memory budgets. A 70B Q4 file is around 43 GB; it may also be possible on 64 GB shared memory with tighter headroom. 120B-class low-bit files need more room and stronger backend validation. Do not infer usability from parameter count alone. |

Catalog sources: [Gemma family](https://deepmind.google/models/gemma/gemma-4/), [Qwen3.5 tags](https://ollama.com/library/qwen3.5/tags), [Qwen3 tags](https://ollama.com/library/qwen3/tags), [Ministral 3 tags](https://ollama.com/library/ministral-3/tags), [Phi-4](https://ollama.com/library/phi4), [Phi-4 Mini](https://huggingface.co/microsoft/Phi-4-mini-instruct), [gpt-oss tags](https://registry.ollama.com/library/gpt-oss/tags), [Llama 3.3](https://ollama.com/library/llama3.3), [Inkling files and runtime requirements](https://huggingface.co/nokeepai/Inkling-2-Mini-Unbound-GGUF). Small Llama and Granite variants are included as existing-suite comparators, not as the preferred Russian assistant.

## What to do with this comparison

For affordable development, the first two tiers can test **Gemma 12B and Qwen3.5 9B**. To test the middle of Pavel's list locally, shortlist **64 GB shared memory**. For broad experimentation across Pavel's entire list, shortlist **128 GB shared memory**, while retaining the runtime qualifications for the largest models.

Start model quality comparisons with **Gemma 31B, Qwen3.8-27B and Qwen3.6-35B-A3B**. Pavel ranks Nemotron first, but its model file and platform requirements make it a more demanding local deployment test. A 31B model passing every test is not established: our paid Gemma API run passed only the two smoke cases, for $0.00067464. Full paid API evaluation is explicitly deferred.

Before any purchase, require a final quote and a run of the exact local artifact with tools on the offered machine. Measure latency, memory, unsafe actions and all 26 GEB cases; inspect all failed cases and repeat promising configurations. Checkpoint, quantization, template and runtime changes can change the score. No offer listed here has been ordered or locally benchmarked by us.
