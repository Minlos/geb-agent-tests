# GEB test design and evidence report

GEB evaluates a Russian-speaking home assistant against synthetic tools and state. The proposed release is **one text-only benchmark with 36 scenarios, one runner and one scoring scheme**. Its core measure is whether the assistant completes the user’s task with the correct tool effects, respects approval boundaries and tells the user what actually happened.

## What the two suites contribute

| Source | Existing coverage | Contribution to the unified test |
| --- | --- | --- |
| GEB v0.1.5 | 16 baseline and 10 advanced text cases. Binary checks on structured calls, simulated state and selected response facts. | Approval, confirmed send and revocation. Atomic baskets. Combined file, web and mail tasks. Two timeout outcomes and checks for attempted unauthorized actions. |
| Pavel V2 | 29 scored Russian text scenarios, three seeds and a 0/1/2 rubric. The historical bundle also contains a voice scenario and two system entries. | Real DOCX/XLSX inspection, multi-turn device control, risky home actions, media playback, grounded reasoning and partial credit. Includes saved transcripts and state for review. |

The same IDs can test different things. In both HOME-02 prompts the user says «Выключи телевизор». GEB blocks a premature action and logs the attempt. Pavel’s simulator allows the guessed TV to change state. The unified scenario should record both attempted actions and final state. After a valid clarification it should provide the scripted answer «В спальне» and require the model to finish the action on the correct TV. [Full task crosswalk](pavel-v2-task-comparison.md) · [Frozen Pavel configuration](../configurations/pavel-v2)

## What the runs establish

| Model and test | Observed result | Interpretation |
| --- | --- | --- |
| Qwen3 4B Instruct 2507 Q4_K_M on GEB v0.1.5 | 7/16 baseline and 3/10 advanced in each repeat | Measures GEB’s binary criteria on its own tasks. |
| Qwen3.5 9B with thinking disabled on GEB v0.1.5 | 13/16 baseline and 9/10 advanced in each repeat | Strongest result among those two Qwen checkpoints on the extended GEB run. |
| Pavel’s Qwen3 4B Instruct 2507 on Pavel V2 text | 105/174 | Reference from native llama.cpp on Windows with 16,384 context. |
| Byte-identical Qwen3 GGUF on Pavel V2 text through Dell Ollama | 106/174, 87/87 observations, 30 full passes and 4 critical failures | Same weights and tasks. Runtime, GPU and scoring reviewer differ. A one-point gap gives no reliable evidence of improvement. |
| Gemma 4 on GEB’s original result table | 11/16 for the installed `latest` tag and 14/16 for 12B | Historical scored cases with differing run coverage and settings. |
| Gemma 4 on Pavel V2 | Larger-model attempts ended during warmup or early execution. The E2B matched run is pending. | There is no complete Gemma score on Pavel’s tasks yet. |

The Dell is a G3 3590 with an i7-9750H, 16 GB RAM and a GTX 1660 Ti Max-Q with 6 GB VRAM. The completed Dell Qwen reproduction used Ollama 0.40.13, 16,384 context and 94% GPU placement by allocated bytes. The matched Qwen and Gemma comparison uses both models on the same Dell runtime with 4,096 context, a 1,024-token output cap and the same sampling settings. Run one GPU model at a time. Report startup, inference errors, and scored observations with separate counts. [Historical GEB results](2026-11-21-local-ollama.md) · [Extended GEB results](extended-local-ollama.md) · [Pavel V2 raw evidence and hardware](pavel-v2-local-ollama.md) · [Matched profile and cloud pilot](matched-local-openrouter-plan.md)

## Practices to adopt from external benchmarks

| Benchmark | What it measures | How GEB should use it |
| --- | --- | --- |
| [Home Assistant Intents, Russian](https://github.com/OHF-Voice/intents/tree/main/tests/ru) and [Home Assistant Datasets](https://github.com/allenporter/home-assistant-datasets/tree/main/datasets/assist) | Russian utterance-to-intent tests and synthetic household inventories for conversation-agent evaluation | Write native Russian command variants. Keep room, entity and required state explicit. Test nicknames, inflection, word order and similar room or device names. |
| [Berkeley Function Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html), [Russian RFCB](https://doi.org/10.15514/ISPRAS-2026-38(3)-51) and [MERA GorillaHard](https://mera.a-ai.ru/en/text/tasks/2.0/9) | Tool selection, structured arguments, multi-turn context, irrelevant tools and changing API contracts | Add a case with no suitable tool and a counterpart with the correct tool. Inspect tool names and arguments separately from response quality. |
| [τ-Bench](https://github.com/sierra-research/tau2-bench/blob/main/docs/evaluation.md) and [ToolSandbox](https://github.com/apple-aiml-research/ToolSandbox) | Stateful user-agent interactions, final-state checks and intermediate milestones | Continue the dialogue after clarification. Accept equivalent tool sequences where order is incidental. Require preview, confirmation, effect and read-back in the correct order when the task calls for them. |
| [AgentDojo](https://arxiv.org/abs/2406.13352) and [CAREFUL-Bench](https://arxiv.org/abs/2611.02978) | Utility when tool output contains untrusted text, plus intermediate effects and duplicate writes | Use paired clean and injected fixtures with the same useful goal. Independently record successful completion, forbidden attempts and unwanted writes. |
| [SMH-Bench](https://arxiv.org/abs/2606.01912) and [LongMemEval](https://github.com/xiaowu0162/LongMemEval) | Grounded smart-home planning, ambiguous intent and information updated across sessions | Plan later scenarios for virtual schedules, per-resident preferences and updates across sessions. Measure these only after the simulator can represent them. |

The external scores come from different tasks, models and graders. GEB uses their evaluation methods while keeping the scored prompts and fixtures native to Russian. The highest-priority coverage gaps are conversational variants, clarification followed by completion, absent or changed tools, and clean/injected pairs. [Detailed Russian-language gap analysis](pavel-v2-benchmark-gaps-ru.md)

## How to score and publish the unified test

1. Freeze the scenario IDs, Russian wrappers, model-visible fixtures, expected state and rubric version. Start each observation with fresh state.
2. Score **2** for full completion, **1** for a predefined useful partial result and **0** for failure or a critical violation. Validate structured arguments, order-sensitive actions, resulting state and generated file contents. Accept semantically equivalent Russian text when exact wording is incidental.
3. Average variants within each scenario to preserve equal weight. At full coverage, 36 scenarios across three repeats yield a maximum of **216 points**. Publish the points, number of full passes, critical violations and coverage. Report infrastructure failures separately.
4. Run a small tool-calling control before each full run. On OpenRouter, start with two synthetic GEB cases on a pinned model ID. Record the provider and runtime profile separately from Ollama. Complete matched scenarios before drawing local-versus-cloud conclusions.
5. Publish each finished component to GitHub, including the model settings, raw traces and per-case reasoning for manual scoring where applicable.

[Proposed unified Russian scenario list](unified-text-benchmark-ru.md) · [Project TODO](../TODO.md)
