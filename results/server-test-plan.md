# OpenRouter and GPU server experiments for household assistant tests

The experiment asks whether Inkling can complete our mail, file, shopping and device tasks reliably, and whether Q8 improves on Q4 enough to justify its memory use. Philip can use the results to decide which models deserve a longer trial. This is a proposed run, not a completed benchmark or a server reservation.

## Two stages

Start with **OpenRouter** to compare task completion with little setup. Then use a **rented GPU server** to test the exact GGUF files, quantization, memory and speed. Both stages remain in the plan. Inkling's exact-file experiment can proceed even if OpenRouter does not offer that model.

| Stage | Question | Proposed usage limit |
|---|---|---|
| 1. OpenRouter | Which available open-weight models complete our tasks reliably? | Free smoke first; up to $5 for approved metered inference |
| 2. GPU server | How do exact Inkling Q4 and Q8 files perform, and what hardware do they need? | Up to $5 total usage and four hours |

The combined proposed usage limit is $10 if both paid stages are approved. Funding deposits, taxes and storage can affect the cash required; check them before spending. Planning does not start either paid stage. API results do not establish local memory needs or throughput, and API quantization labels do not identify an exact GGUF file.

## Stage 1: OpenRouter

Use the [matched Dell and OpenRouter plan](matched-local-openrouter-plan.md) for the initial command and model IDs. Recheck availability, prices and structured-tool support immediately before running. Start with its free Gemma endpoint, then the listed Qwen3.5 9B metered candidate if approved. These checkpoints differ from Pavel's Qwen3 4B. Add at most one further open-weight candidate with plausible self-hosting memory requirements; document those requirements before including it. A free endpoint is a useful capability comparison even if it is too large for the intended home hardware.

1. Supply a dedicated API key via `OPENROUTER_API_KEY` in the local environment. For metered runs, set a non-resetting $5 key spending cap and verify it before requests. Account deposits are separate from inference usage. [OpenRouter key limits](https://openrouter.ai/docs/api/api-reference/api-keys/create-a-new-api-key).
2. Run MAIL-01 and HOME-02; inspect structured calls and tool results. If transport and tool integration work, retain behavioral failures and continue the pilot rather than requiring a perfect smoke score.
3. Run the same 16 baseline and 10 advanced cases as stage 2, one repeat first and two additional repeats within the approved budget. Preserve all attempts. Use the same suite commit, grader, prompts, tool schemas, temperature, output cap and timeout across the comparison; record unsupported settings explicitly.
4. Record exact model ID, actual provider, timestamp, request IDs, available usage/cost data and thinking settings. Prefer a fixed provider with fallbacks disabled for a controlled comparison. The current runner does not expose OpenRouter's `provider` routing object; configure and verify routing through a supported preset or add and validate that support before claiming a provider-pinned run. Otherwise label results as default routing and record the provider when available. [Provider routing](https://openrouter.ai/docs/guides/routing/provider-selection).
5. Verify thinking controls against the chosen endpoint. The runner's top-level `reasoning_effort` option is not proof that OpenRouter and its provider honor the request. If control is unverified, label thinking as unknown and do not call it a matched non-thinking run.
6. Export raw JSON and an API results table with pass counts, unsafe attempts, empty/truncated responses, rate-limit/errors, elapsed time and actual cost. Record missing provider metadata as unknown. Rate-limit failures remain missing observations, separate from task failures.

All API fixtures are synthetic. Run inference on the existing computer; renting a server is unnecessary for this stage. Pavel's 29-case suite is a separate comparison with its own runner and rubric. The proposed unified 36-case benchmark is not substituted until implemented and verified.

## Stage 2: exact GGUF and hardware experiment

Use the server procedure below after the API pilot, or to resolve exact-file questions the API cannot answer. Keep API and server results in separate rows. Select a promising API model for later self-hosting only after checking its weights, license and memory needs against the 400,000-ruble installation budget; a 48 GB rental is an experimental resource, not a validated home purchase.

## Hardware and spending

Use one on-demand NVIDIA A40 or RTX A6000 with 48 GB VRAM, at least 48 GB system RAM and about 120 GB temporary disk. Load one model at a time. Start at 4,096 context tokens, one request at a time, and verify actual full GPU placement and remaining memory. Q8 weights are 27.8 GB; runtime memory is additional. BF16 weights are 52.2 GB and are outside this first experiment.

[Runpod's published pricing](https://www.runpod.io/pricing) currently lists A40 at $0.59/hour and RTX A6000 at $0.69/hour. Recheck the actual offer, availability, disk charges, taxes and any minimum deposit before launch. A four-hour allocation would cost $2.36 or $2.76 for GPU compute alone. Propose a **$5 total usage limit and four-hour maximum**, including setup and downloads; these are limits for approval, not an automatic billing cap or a guarantee of completion. Allow roughly 1–2 hours for initial setup and compatibility checks; inference duration is not yet measured.

Use temporary storage and export evidence before terminating the instance. A stopped instance can retain billable storage; verify remaining volumes and charges after cleanup. The existing small VPN server is not the GPU host for this experiment.

## Configurations

| Configuration | Purpose |
|---|---|
| Inkling-2-Mini-Unbound Q4_K_M | Test Pavel's suggested model at a relatively practical memory size |
| Inkling-2-Mini-Unbound Q8_0 | Measure the quality and speed difference from Q4 on the same GPU |
| Qwen3.5:4b, thinking disabled | Repeat our Dell configuration on the server as a comparison |

Use [the publisher's exact Inkling GGUF files](https://huggingface.co/nokeepai/Inkling-2-Mini-Unbound-GGUF): `Inkling-2-Mini-Unbound-Q4_K_M.gguf` and `Inkling-2-Mini-Unbound-Q8_0.gguf`. Record repository revision and file hashes. Pin a CUDA llama.cpp build that includes the loop fix referenced in the card (PR #32704); check the build and template rather than assuming a bundled runtime supports it.

For Qwen, preserve the Dell model digest, quantization and Ollama version/settings where possible. If a different runtime is needed, label that comparison as a combined hardware/runtime change. Do not attribute any score difference solely to the GPU. These 26 cases are separate from Pavel's supplied 29-case suite and do not reproduce its scores.

## Execution order

1. Record the rental price and instance specifications, repository commit, GPU driver, runtime build, model hashes, templates, context allocation and sampling settings. Use the same suite and grader for all configurations. Keep mail and files synthetic.
2. Verify each endpoint accepts structured tools. Run MAIL-01 and HOME-02 and inspect calls and tool results. Distinguish an unsupported architecture/template/API from a model that calls the wrong tool or fails the task.
3. Verify Inkling's thinking control in the installed build. Start at the lowest documented effort and retain actual reasoning and final-answer output. The publisher says effort 0 can still think briefly. Keep this setting identical between Q4 and Q8; do not assume Qwen's `--no-thinking` has the same meaning.
4. Run one repeat of all 16 baseline and all 10 advanced cases for each supported configuration, separately. Keep temperature 0, a 1,024-token output limit and 300-second request timeout to match the existing experiment. Record any other limits. If outputs hit the cap, retain these results; a larger-cap run is a separately labelled experiment for both Inkling quantizations.
5. If time and spending allow, add two repeats of each suite to reach three repeats. Three configurations with 26 cases and three repeats total 234 case executions, excluding smoke checks. Report incomplete runs with their actual denominator; do not silently omit failures or timeouts.
6. Save raw JSON, original API responses, runtime logs, peak RAM/VRAM and GPU placement. Record elapsed case time and server-reported generation metrics separately. Report time to first token only if measured; total case time is not tokens per second.
7. Review passes and failures, especially secret access, injected instructions, unconfirmed sends, revoked approvals and false claims of completion. Publish full-pass counts per repeat, unsafe attempts, truncated/empty answers and timeouts. Export evidence and terminate the instance within the agreed limits.

## Runner commands

Run the runner on the GPU host against the loopback endpoint, or use an SSH tunnel from the client. Keep the inference port private. After setting the endpoint's actual served model name:

```bash
export BENCH_BASE_URL=http://127.0.0.1:8080/v1
export BENCH_MODEL=actual-served-model-name
export BENCH_LABEL=inkling-q4

python3 run_tests.py --base-url "$BENCH_BASE_URL" --model "$BENCH_MODEL" \
  --only MAIL-01,HOME-02 --max-tokens 1024 --timeout 300 \
  --output "runs/server-${BENCH_LABEL}-smoke"

python3 run_tests.py --base-url "$BENCH_BASE_URL" --model "$BENCH_MODEL" \
  --repeat 1 --max-tokens 1024 --timeout 300 \
  --output "runs/server-${BENCH_LABEL}-baseline-pilot"

python3 run_tests.py --base-url "$BENCH_BASE_URL" --model "$BENCH_MODEL" \
  --advanced --repeat 1 --max-tokens 1024 --timeout 300 \
  --output "runs/server-${BENCH_LABEL}-advanced-pilot"
```

Change the label for every configuration or additional run. Configure Inkling's effort through its verified runtime/template control. For the compatible Qwen endpoint, add `--no-thinking`. Use `--repeat 2` with new output folders for the additional repeats and retain the pilot. Never compare only the best repeat.

Launch remains pending Philip's approval of the provider and usage limit. No paid resource is needed to review this plan. If Inkling proves useful, a later original-versus-Unbound comparison can test whether the modification affects our task and safety results. Cloud performance alone does not establish that a complete home installation fits the 400,000-ruble budget.
