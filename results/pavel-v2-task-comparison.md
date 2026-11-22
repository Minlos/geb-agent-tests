# GEB task comparison

## Existing suites

The GitHub suite v0.1.5 contains 16 baseline and 10 advanced text cases. It uses deterministic assertions over arguments, simulator state, attempted operations and selected response text. Pavel V2 contains 29 scored Russian text scenarios plus a voice scenario and two unscored system entries. Its original text reference is **105/174 (60.3%)** over seeds 42, 43 and 44. Reviewers assign 0, 1 or 2 points against per-case rubrics and record critical failures. The full reference, including speech, is 60.2/100. Both simulate tools and use synthetic data.

The matching Qwen3 4B Instruct 2507 checkpoint scored 7/16 baseline and 3/10 advanced on GitHub v0.1.5 in each repeat. Those counts measure different scenarios and use a different grading scale. The same-task comparison uses Pavel's 29 text scenarios and Pavel's rubric, with runtime details recorded separately.

| Capability | GitHub v0.1.5 | Pavel V2 | Merge decision |
| --- | --- | --- | --- |
| Mail search and drafts | MAIL-01/02 delivery facts and exact draft | MAIL-01/02 date range, meeting facts and courtesy draft | Use range filtering and distractors. Include both exact-copy and intent-based draft requirements. |
| Confirmation lifecycle | MAIL-03/04 and ADV-06 cover preview, identical confirmed send and revocation | MAIL-03 combines reading, drafting and preview in a single flow | Use a shared fixture and three independent branches. |
| Grounding and reasoning | WEB-01 and ADV-04 cover conflicting hours and their overlap. ADV-09 resolves dated revisions. | WEB-01/02 cover dates and conflicting prices. LLM-01/02/03 cover measurement concepts, missing facts and planning. | Require both source citations and conflict reporting in one case. Keep synthesis and the three reasoning skills. |
| Untrusted content | WEB-02, FILE-04, ADV-05, ADV-08 and ADV-10 carry instructions in pages, files, mail and catalog | WEB-03 and FILE-04 exercise pages and files | Keep four carrier cases. Combine file and web inputs in the synthesis case. |
| Files and workspace | FILE-01/02/03 cover extraction, CSV aggregation and workspace escape | FILE-01/02/03 add quotations, valid DOCX/XLSX and absolute path | Inspect content in generated files and preserve a dedicated confinement case. |
| Device state | HOME-01/02, ROBUST-01, ADV-02 cover verified state, ambiguity and both timeout outcomes | HOME-01 is multi-turn on/off. HOME-02 allows the wrong TV to change state. HOME-03 gates a risky action. ROBUST-01 leaves outcome uncertain. | Check on and off across turns, clarification before mutation, risky-action approval, and separate timeout fixtures for committed and uncommitted outcomes. |
| Shopping and payment | SHOP-01/02 and ADV-03/07 cover price limits and atomic bundles | SHOP-01/02 require preview order and no unwanted substitution. SHOP-03 gates payment. | Keep preview and add, no matching item, feasible bundle, infeasible bundle and payment gate. |
| Privacy and unsafe requests | SEC-01 requires an explicit redaction marker | SEC-01/03/04 and PRIV-02 cover protected preview, static inspection, unsafe commands and external transfer approval | Check non-disclosure across replies and tool arguments. Keep external transfer, inspection and destructive request cases. |
| Playback and correction | No equivalent | CONTENT-01/02 and EXTRA-01/02/03 | Keep mock playback and explicit correction, revised constraints and contradiction detection. Use written prompts throughout. |
| System and audio | Outside these 26 cases | VOICE-01, SEC-02, PRIV-01 | Exclude from the scoring list. |

