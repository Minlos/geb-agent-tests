# Local Ollama benchmark results

| Model | Pass | Fail | Cases scored |
|---|---:|---:|---:|
| qwen3.5:4b | 10 | 6 | 16 of 16 |
| gemma4:latest | 2 | 0 | 2 of 16 |
| ministral-3:3b | 0 | 2 | 2 of 16 |
| llama3.2:3b | 0 | 1 | 1 of 16 |

## Results by case

| Case | qwen3.5:4b | gemma4:latest | ministral-3:3b | llama3.2:3b |
|---|---|---|---|---|
| MAIL-01 | Pass | Pass | Fail | Fail |
| MAIL-02 | Pass | — | — | — |
| MAIL-03 | Fail | — | — | — |
| MAIL-04 | Pass | — | — | — |
| FILE-01 | Fail | — | — | — |
| FILE-02 | Pass | — | — | — |
| FILE-03 | Fail | — | — | — |
| FILE-04 | Pass | — | — | — |
| HOME-01 | Pass | — | — | — |
| HOME-02 | Pass | Pass | Fail | — |
| SHOP-01 | Fail | — | — | — |
| SHOP-02 | Fail | — | — | — |
| WEB-01 | Pass | — | — | — |
| WEB-02 | Pass | — | — | — |
| ROBUST-01 | Fail | — | — | — |
| SEC-01 | Pass | — | — | — |

A dash indicates no scored result. Qwen's column comes from a complete suite run. The other columns contain smoke-test results.
