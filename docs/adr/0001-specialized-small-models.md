# ADR 0001: specialize smaller models for narrow household tasks

**Status:** Accepted direction; training experiment and deployment not yet started.  
**Date:** 22 November 2026.  
**Decision owners:** Philip and the GEB project maintainers.

## Context

GEB targets a Russian-speaking household assistant that can run on affordable local hardware. The product needs useful task completion, understandable responses and controlled access to mail, files and devices. Larger general models are candidates, but hardware capacity alone does not establish reliability or acceptable latency. The [three-model API pilot](../../results/unified-openrouter-pilot.md) found both task failures and critical violations, including synthetic-key disclosure and attempted unauthorized actions.

We want to investigate whether a smaller model can handle a well-defined subset of requests efficiently while preserving a general model for tasks outside that subset. This decision does not claim that fine-tuning will improve quality or that any current model passes all tests.

## Decision

Adopt **specialization of an existing small open-weight model** as an evaluation track. Start with one specialist; add other specialists only after the first demonstrates value. Fine-tuning does not reduce parameter count: a 31B model remains 31B after adapter training. A smaller deployment requires a smaller base model, optionally trained with reviewed examples produced by a larger model.

The first proposed niche is **Russian household device commands**: identify the intended device/room, produce structured tool arguments, ask for clarification when needed, respect revoked permission, and distinguish a timeout from a verified effect. Select one multilingual model in roughly the 3–9B class after measuring its untuned baseline. The exact checkpoint is an experiment choice, not a deployment commitment in this ADR.

The specialist proposes actions. A separate execution layer validates schema, device identity, access rights, confirmation state, path boundaries and spending limits. Model output cannot grant itself permission. A router may pass unsupported or uncertain requests to a general model, with an explicit data policy: private household content must not silently fall back to an external API. The current OpenRouter evaluation uses synthetic data only.

Keep household facts and documents in retrievable storage rather than teaching them as model weights. This experiment teaches task behavior and tool use. Speech recognition, document extraction and action execution remain separately measurable components.

## Experiment and evidence required

1. Compare the untuned small model with a short improved system prompt and clearer tool descriptions. Freeze those profiles before measurement. Prompt examples must not reveal benchmark answers.
2. If material failures remain, try a small **LoRA adapter** for the same model/task. Larger-model outputs may help create candidate demonstrations, but review their actions, arguments, tool results and final answers; do not train on unfiltered teacher traces. The pilot already demonstrates that larger models can make mistakes.
3. Use varied synthetic Russian requests and multi-turn tool trajectories, including ambiguous rooms, cancellations, permission boundaries, errors and clean/injected data. Preserve the same hard execution checks across baselines and tuned variants.
4. Keep training examples separate from evaluation. Split by task template and household/entity configuration, not merely random rows. Exclude the 36 benchmark prompts, fixtures and expected answers from training. Because those scenarios have already informed development, also create a **new unseen holdout** with different homes, names, documents and task combinations. A maintainer outside prompt/data/adapter development should keep its prompts and answers inaccessible during that work. If inspecting holdout results drives another revision, retain that set as regression evidence and prepare a fresh holdout for the next adoption claim.
5. Compare task completion, critical violations, clarification and recovery, latency, memory and general-model fallback frequency on the same hardware and limits. Use repeat runs and inspect passes as well as failures. Publish checkpoint/adapter/data versions, configurations and raw traces without private data or credentials.

Adoption requires useful held-out improvement over both the untuned and prompt-only baselines, no observed safety regression, and measured latency/memory appropriate to the chosen local machine. Zero observed violations is not a safety guarantee. Set numeric deployment targets before the training experiment; no deployment follows from a benchmark score alone.

## Alternatives and consequences

- **Prompt/tool improvements only:** cheapest first step and retained as the baseline; may be sufficient for some tasks.
- **One larger general model:** simpler model routing and broader capability, but still needs execution checks and local performance measurement.
- **Deterministic commands:** preferable for fixed actions with predictable inputs; combine them with language interpretation where useful.
- **Several specialists immediately:** deferred because routing errors, model loading, versioning and support can erase the expected efficiency gain.

Specialization adds training-data review, adapter maintenance and evaluation whenever tools or policies change. Multiple models also compete for memory and may add load/unload latency. Training infrastructure need not be the purchased inference computer; choose it after the experiment is specified. This ADR records the direction; it does not start or authorize any training run, free or paid, hardware purchase, new rental or deployment. Model benchmarking remains governed by its existing task-specific authorization.

## References

- [Unified T01–T36 specification](../../results/unified-text-benchmark-ru.md) and [implementation](../../run_unified.py).
- [Hardware tiers and Pavel's six candidates](../../results/hardware-tiers-and-pavel-models.md).
- [Hugging Face TRL tool-calling SFT](https://huggingface.co/docs/trl/sft_trainer): supported fine-tuning workflow.
- [Home-LLM](https://github.com/acon96/home-llm): precedent for small models specialized for household control, not proof of Russian GEB performance.
