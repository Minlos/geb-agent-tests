# Extended local Ollama benchmark

Runs in this report use the 16 baseline cases and the ten advanced cases from suite v0.1.5. The [original five-case results](advanced-local-ollama.md) remain separate. The [testing plan](../TODO.md) calls for one model at a time, two smoke checks, and three repeats per suite.

## Qwen3 4B Instruct 2507

| Field | Observed value |
|---|---|
| Ollama tag | `qwen3:4b-instruct-2507-q4_K_M` |
| Model digest | `0edcdef34593eac1aa2be9c7d06c432dcf81945adca5eca2f27662c18f168ba0` |
| Quantization and package | Q4_K_M, 2.50 GB |
| Runtime and context | Ollama 0.40.13, 4,096-token active context |
| GPU placement | Ollama reported the full loaded allocation in GPU memory |
| Request settings | Temperature 0, 1,024 max output tokens, 300-second API timeout, no thinking override |

The two smoke cases returned structured tool calls. MAIL-01 stopped after search without reading the message. HOME-02 attempted to turn off a TV before asking which TV was intended. The simulator blocked the action. Both smoke cases failed on task behavior.

The full baseline and advanced runs are in progress. This is a checkpoint comparison with Pavel's reported Qwen3 model. His exact artifact, quantization, runtime and runnable test code are still needed for a reproduction.
