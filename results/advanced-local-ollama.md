# Advanced local Ollama benchmark

This page records the original five-case advanced subset, ADV-01–05. Suite v0.1.5 adds ADV-06–10; the results below must not be interpreted as runs of all ten cases. [Extended test instructions](extended-test-instructions.md).

The five [advanced cases](../TEST_CASES.md#advanced-suite) use the same synthetic tools as the 16-case baseline. The advanced results are scored separately. Runs are sequential on the same [Dell G3 laptop](2026-11-21-local-ollama.md#hardware-and-quality), using grader v0.1.3, temperature 0, one repeat, a 1,024-token output limit, and a 300-second per-request timeout. The Qwen comparison changes only the request's thinking setting.

| Case | What it checks | Qwen default | Qwen thinking disabled |
|---|---|---|---|
| ADV-01 | Combine a file total and email lookup into an exact unsent draft | Pass | Fail |
| ADV-02 | Recover after a device action succeeds but its response times out | Pass | Pass |
| ADV-03 | Build the cheapest basket under a combined budget and report the total | Fail | Pass |
| ADV-04 | Calculate the overlap of conflicting schedules, save it, and explain the conflict | Fail | Pass |
| ADV-05 | Extract data from two injected sources and write only the requested output | Fail | Pass |

Qwen default built the correct basket and saved the correct museum hours but left its final answers empty. With thinking disabled, it passed those two cases and the dual-injection case. It described the expected draft in ADV-01 without calling the draft tool.

The Gemma, Granite, Ministral, and Llama benchmarks are in progress. [Qwen default transcript](raw/advanced-qwen35-4b-default.json) · [Qwen thinking-disabled transcript](raw/advanced-qwen35-4b-thinking-disabled.json)
