# GPU server experiment for household assistant tests

The experiment asks whether Inkling can complete our mail, file, shopping and device tasks reliably, and whether Q8 improves on Q4 enough to justify its memory use. Philip can use the results to decide which models deserve a longer trial. This is a proposed run, not a completed benchmark or a server reservation.

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

For Qwen, preserve the Dell model digest, quantization and Ollama version/settings where possible. If a different runtime is needed, label that comparison as a combined hardware/runtime change. Do not attribute any score difference solely to the GPU. This run does not reproduce Pavel's private test suite.

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
