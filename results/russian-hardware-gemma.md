# Gemma and a ₽200,000–400,000 computer in Russia

The decision is which Gemma models deserve a local trial within the budget for a complete computer. Retail pages checked on 22 November 2026 support a shortlist of **Gemma 4 12B, 26B-A4B and 31B**. A standalone 4B model is not the hardware ceiling of this budget. None of these configurations has yet demonstrated full completion of our tests locally.

## Hardware offers and model candidates

Prices below are public seller listings, not confirmed quotes or purchase recommendations. Delivery, installation, operating-system licenses, microphones and home-device integration may add to the total.

| Route | Observed Russian listing | Gemma candidate and practical limit |
|---|---|---|
| New desktop with 16 GB GPU | КВАНТ lists Ryzen 5 5600, RTX 5060 Ti 16 GB, 16 GB system RAM and 1 TB SSD for ₽162,667, or ₽152,933 cash. Its description also mentions a different GPU, so the exact bill of materials needs confirmation. | Gemma 4 12B Q4 or Q6. Increase system RAM to at least 32 GB, preferably 64 GB; obtain the upgrade quote before treating it as a complete AI build. The larger models below do not fit entirely in 16 GB VRAM at these Q4 sizes. |
| Shared-memory mini PC | FEVM FAEX1, Ryzen AI Max+ 395, 64 GB shared RAM and 2 TB SSD: ₽235,500; 128 GB and 2 TB: ₽319,000. The latest seller page lists both under order, about 10 days. | Gemma 26B-A4B or 31B, including larger quantizations. Memory capacity is promising; GPU allocation, runtime support, sustained latency and noise remain unmeasured. Shared RAM is not equivalent in speed to dedicated VRAM. |
| Custom desktop with 24 GB GPU | Полюс lists an AFOX RTX 3090 24 GB at ₽248,686 for the card alone. This leaves ₽151,314 of a ₽400,000 budget for all other parts and services, by subtraction. | Gemma 26B-A4B Q4 or 31B Q4 at a modest initial context. A complete compatible build has not been priced; card price and supply require confirmation. The allocation is not a quoted bill of materials. |
| RTX 4090 prebuilt | Firestrike's listed Core i5-13600KF / RTX 4090 / 32 GB / 1.5 TB model costs ₽531,720. | Exceeds the total budget in this checked offer. Do not assume a new 4090 computer fits the ceiling. |

Sources: [КВАНТ exact configuration](https://quantcomputers.ru/product/5600-16-1000-5060ti16gb-whh/), [FEVM configurations](https://www.fevm.store/products/faex1/), [Полюс RTX 3090](https://polus.ru/videokarty-komplektuyuschie/afox/af3090-24gd6xh7-3198449), [Firestrike RTX 4090 computers](https://www.firestrike-pc.ru/collection/igrovye-pk-rtx-4090).

The GPU cards and computers are different purchase scopes. None of these prices includes a demonstrated GEB installation. At the ₽200,000 end, a new 16 GB GPU system with the 12B model is the clearer candidate. At roughly ₽300,000–400,000, shared-memory systems provide a plausible route to 26B/31B without relying on an unverified cheap used GPU.

## Model memory and test evidence

Published converter files put Gemma 4 12B Q4_K_M at about **7.38 GB**, 26B-A4B Q4_K_M at **16.80 GB**, and 31B Q4_K_M at **18.69 GB**. These are weight-file sizes, not total memory. Add context cache, runtime buffers and any vision components. Start local trials at 4,096 context tokens, one request at a time, and measure actual allocation before increasing context.

Sources: [12B GGUF files](https://huggingface.co/lmstudio-community/gemma-4-12B-it-GGUF/tree/main), [26B-A4B GGUF files](https://huggingface.co/lmstudio-community/gemma-4-26B-A4B-it-GGUF/tree/main), [31B GGUF files](https://huggingface.co/lmstudio-community/gemma-4-31B-it-GGUF/tree/main).

**26B-A4B is not a standalone 4B model.** It has approximately 26B total parameters with roughly 4B active per token; the weights still need memory. Google's documentation positions it as a faster alternative to the dense 31B. This does not guarantee a particular speed or score on our tasks. [Google model card](https://huggingface.co/google/gemma-4-26B-A4B-it).

The paid `google/gemma-4-31b-it` API endpoint passed MAIL-01 and HOME-02, one attempt each. It retrieved the delivery details and asked which TV to switch off. Reported request costs sum to **$0.00067464**. This is evidence for the API smoke only: its quantization and hardware are not the local GGUF configuration, and 24 remaining GEB cases were not tested in this run. [Smoke evidence](openrouter-smoke.md).

## Which configuration to test first

1. Use **Gemma 4 31B as the larger quality candidate** and **26B-A4B as the speed candidate**, with 12B as the less demanding alternative. No model can be promised to pass the suite from its parameter count. Inspect failures before deciding whether model capacity, the template, tools or grading caused them.
2. For a new compact machine within budget, investigate the **128 GB FAEX1 / 2 TB listing** first. It leaves more memory for Q8, documents and other processes than the 64 GB version. This is a shortlist decision; seller reliability, delivered configuration, warranty and runtime performance have not been independently verified.
3. For a CUDA desktop, obtain a complete 24 GB GPU build quote and a measured trial before choosing it over shared memory. Used RTX 3090 listings need separate inspection and current availability confirmation. Search snippets at low prices were often stale, out of stock or unavailable on opening; no cheap used listing is treated as secured supply.
4. Before purchase, run the exact local Q4 file on the target machine with all 36 unified scenarios. Record completion, unsafe attempts, latency and peak memory. If acceptable, repeat three times and check the real document and voice pipeline. More memory establishes capacity, not acceptable response time.

Philip has authorized one unified36 OpenRouter pilot per selected checkpoint, with a $1 aggregate cap; exact local GGUF trials remain separate. No hardware has been ordered, no seller contacted and no GPU instance rented. The next purchase decision needs an actual local performance measurement and a final complete quote.
