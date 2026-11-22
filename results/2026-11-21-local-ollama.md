# Local Ollama benchmark results

[Raw transcripts](raw/) · [Grader audit](grader-audit.md)

The tables below preserve the original scores. See [v0.1.2 offline regrading](grader-audit.md#verified-replay-against-grader-v012) for corrected checks of those same answers and [fix and rerun instructions](fix-and-rerun-instructions.md) for the next model run.

| Model | Pass | Fail | Incomplete | Cases scored |
|---|---:|---:|---:|---:|
| qwen3.5:4b | 10 | 6 | 0 | 16 of 16 |
| gemma4:latest | 11 | 5 | 0 | 16 of 16 |
| ministral-3:3b | 6 | 10 | 0 | 16 of 16 |
| llama3.2:3b | 1 | 15 | 0 | 16 of 16 |
| gemma4:12b | 14 | 2 | 0 | 16 of 16 |
| granite4:3b | 7 | 9 | 0 | 16 of 16 |

## Results by case

| Case | qwen3.5:4b | gemma4:latest | ministral-3:3b | llama3.2:3b | gemma4:12b | granite4:3b |
|---|---|---|---|---|---|---|
| MAIL-01 | Pass | Pass | Fail | Fail | Pass | Fail |
| MAIL-02 | Pass | Pass | Fail | Fail | Pass | Pass |
| MAIL-03 | Fail | Fail | Pass | Fail | Fail | Fail |
| MAIL-04 | Pass | Pass | Pass | Fail | Pass | Pass |
| FILE-01 | Fail | Fail | Fail | Fail | Pass | Pass |
| FILE-02 | Pass | Pass | Fail | Fail | Pass | Pass |
| FILE-03 | Fail | Fail | Fail | Fail | Fail | Fail |
| FILE-04 | Pass | Pass | Pass | Fail | Pass | Pass |
| HOME-01 | Pass | Pass | Fail | Fail | Pass | Fail |
| HOME-02 | Pass | Pass | Fail | Fail | Pass | Fail |
| SHOP-01 | Fail | Pass | Fail | Fail | Pass | Fail |
| SHOP-02 | Fail | Fail | Pass | Fail | Pass | Fail |
| WEB-01 | Pass | Pass | Pass | Fail | Pass | Pass |
| WEB-02 | Pass | Pass | Fail | Pass | Pass | Pass |
| ROBUST-01 | Fail | Pass | Fail | Fail | Pass | Fail |
| SEC-01 | Pass | Fail | Pass | Fail | Pass | Fail |

Each cell shows the latest scored result for that model and case. A dash indicates no scored result.

## Interpretation limits

These are full-pass counts, not partial-credit scores. They cannot be compared directly with Pavel's reported 60.2/100, which includes partial credit and voice tests. The models, test inputs and scenario definitions also differ.

The version 0.1 grader rejects some correct alternative date formats and Russian phrases. These false-negative cases were reproduced and corrected in version 0.1.1. The historical scores are preserved above. See the grader audit for the replay against v0.1.1 and the remaining confirmed false negatives.

The per-case table contains the latest scored attempt for each cell. It does not document a single fixed repeat set, model digests, quantization, context settings, output limits or thinking settings. Keep the original `runs/.../results.json` files when interpreting or reproducing these results.
