# Engineering. All five targets exist from M00 PR 1 and run from M00 PR 2
# (SPEC/00 §8 M00). `ledger-plain` is the sixth, from M00 PR 2: GNU make
# takes `--plain` for an option of its own, so `make ledger --plain` could
# never run (ADR-0004).
#
# The chain is the same in CI and locally (P5): the runners write raw
# observations, cost-cap prints the spend, verdict.build writes the card and
# the envelope, verdict.gate rules on the envelope. A recipe that fails
# exits 1 (gate: 1 RED, 2 REJECTED; build: 3 REFUSED); GNU make then exits 2.
#
# From M01 (ADR-0004 amendment 2) an envelope has one subject: the agent
# when one ran, otherwise the control, in M00's form. The control runs every
# time (P6) and its card is written first. Until an agent runner is in the
# tree (M01 PR 2) there is no agent under test, so the envelope is the
# control's. A run always writes an envelope.
#
# From M01 PR 2 `src/agent/run.py` is in the tree, so both run: the control
# writes the card, refagent writes the envelope, and cost-cap adds the two
# up against one cap (ruling l).

.PHONY: evals evals-local validate plants ledger ledger-plain

COMMIT := $(shell git rev-parse HEAD)
HISTORY := evals/history
LOCAL := evals/local
AGENT_RUNNER := $(wildcard src/agent/run.py)

# CI passes these. Each becomes an entry in the envelope's `checks`.
# M01 PR 2 adds claim 1's (SPEC/01 §4). F1_1 is read from two sources and
# passes only if both do: the S1, S2, S3 and S8 tests, and CloudTrail's
# record of S4's attempts. F1_2 is the S5 test. F1_3 is CloudTrail's record
# of S6's attempt. F1_4 is the envelope's own goldens and needs no flag.
F0_2_JUNIT ?=
F0_3_OBS ?=
JUNIT ?=
S4_OBS ?=
S6_OBS ?=
RUN_URL ?=
F1_1_CASES := test_s1_an_unsigned_bundle_is_refused,test_s2_a_bundle_changed_after_signing_is_refused,test_s3_egress_not_in_the_manifest_is_refused_at_synth,test_s8_an_agent_outside_the_construct_is_refused_at_synth
F1_2_CASES := test_s5_a_role_without_the_boundary_is_refused_at_synth
# M02 PR 2 (SPEC/02 §4). F2_1's first source: the five seed tests that apply
# a seed to a copy of the tree and ask src/gates/ and validate to refuse it
# (S1 both forms, S2, S3, S5). Its second source, the seed PRs and the
# owner's attempts as GitHub recorded them (scripts/observe_pr.py), and
# F2_2, the three doors, are wired by evals.yml at PR 3 through the three
# observation variables below; both() then passes F2_1 only if both sources
# do. S4's test is not in the list: it reads what the human typed and is
# the weaker witness (f2_1_bypass.yaml), and its marker stays until the
# attempts are made.
F2_1_CASES := test_s1_one_key_on_a_relaxation_is_refused,test_s1_two_files_from_one_seat_are_one_key,test_s2_a_golden_edited_to_green_a_build_is_refused,test_s3_a_one_sided_edge_is_refused,test_s5_a_renamed_golden_id_is_refused
SEED_PRS_OBS ?=
BYPASS_OBS ?=
DOORS_OBS ?=
# M03 PR 2 (SPEC/03 §4, §5.1). F3_1, F3_2, F3_3 and F3_6: each seed refused
# in a copy of the tree, read from the tests, with the guards beside the two
# falsifiers they hold (a regressed golden RED; a never-passed one not). F3_5:
# CI's lookup of seed S5's attempt (scripts/observe_ingest.py).
F3_1_CASES := test_s1_a_table_change_is_not_measured_against_mains_table,test_f3_1_guard_a_regressed_golden_is_red
F3_2_CASES := test_s2_a_silent_red_team_plant_is_red
F3_3_CASES := test_s3_a_golden_that_overlaps_the_corpus_is_refused
F3_6_CASES := test_s6_a_control_added_later_does_not_re_rule_an_old_envelope,test_s7_a_pass_recorded_later_does_not_re_rule_an_old_envelope,test_f3_6_guard_a_never_passed_golden_is_not_red
INGEST_OBS ?=
# M04 PR 2 (SPEC/04 §4). F4_1, F4_2 and F4_4: each seed refused in a copy of
# the tree, read from the tests; F4_1 and F4_2 from the tests alone are
# test-only witnesses until PR 3 wires the swap PRs as their second source. F4_4 is
# joined by build's own reading of the bars. F4_3: the S3 test and the run's
# own two runs, only when A_VS_A is set: the job then runs each subject twice
# and hands build the second runs.
F4_1_CASES := test_s1_a_breaking_swap_whose_answers_the_tool_never_grounded_is_red
F4_2_CASES := test_s2_the_equivalent_swaps_pin_is_one_the_eval_role_may_invoke
F4_3_CASES := test_s3_two_runs_of_one_pin_that_differ_are_a_failed_a_vs_a
F4_4_CASES := test_s4_a_run_over_the_incumbents_bar_is_red[s4-slow-raw.json-p95-latency_ms-3],test_s4_a_run_over_the_incumbents_bar_is_red[s4-heavy-raw.json-tokens-usage-2]
A_VS_A ?=
# M04 PR 3 (SPEC/04 §4): the swap PRs, as observe_pr.py recorded them from
# milestones/M04/runs/f4_swaps.yaml. rule_swaps.py has the gate rule each
# one's own envelope, in a scratch worktree of HEAD, and build copies the
# verdicts into the envelope's `swaps`. Recorded, never gated (Product, M04
# PR 3): F4_1 and F4_2 stay the seed tests' witnesses. From M05 PR 1 evals.yml
# no longer passes it (milestones/M05/open.md row 1): the swap PRs are closed,
# and row 4 reads its own envelope. Empty, the step is skipped.
SWAPS_OBS ?=
SWAPS_RULED = $(SWAPS_OBS:.json=-ruled.json)
# M05 PR 2 (SPEC/05 section 4). F5_1: seeds S4 and S5 refused by their readers,
# read from the two tests, a test-only witness; the only claim 5 check on an
# envelope. The live attempts are CONTAINMENT_OBS, scripts/observe_containment.py's
# reading of the audit bucket: build records them in `containment` and
# `alarm_latency_s`, and only the ledger's row 5 reading reads them. Empty,
# the envelope has no containment, and row 5 reads it as not read.
F5_1_CASES := test_s4_a_chain_at_depth_3_is_refused_before_the_model,test_s5_an_answer_that_repeats_a_credential_from_a_tool_result_does_not_pass
CONTAINMENT_OBS ?=
# M06 PR 2 (SPEC/06 section 4). F6_1: seeds S1a and S1b refused by their own
# readers and neither by the other's; F6_4: seed S4 refused by the panel query
# reader and found by build's comparison. Test-only witnesses, the only claim 6
# checks on an envelope. The live records are TEMPLATE_OBS,
# scripts/observe_template.py's reading of GitHub, AWS and Grafana: build rules
# them into `template`, and only the ledger's row 6 reading reads it. Empty,
# the envelope has no template, and row 6 reads it as not read.
F6_1_CASES := test_s1a_an_unassigned_seat_is_refused,test_s1a_reader_does_not_refuse_s1b,test_s1b_goldens_under_the_minimum_are_refused,test_s1b_reader_does_not_refuse_s1a
F6_4_CASES := test_s4_a_panel_1_query_with_a_second_source_is_refused,test_s4_a_panel_row_with_no_registry_row_is_found_by_build
TEMPLATE_OBS ?=
CHECKS := $(if $(F0_2_JUNIT),--check-junit F0_2 tests.test_f0_2 "$(F0_2_JUNIT)") \
          $(if $(F0_3_OBS),--check-pr F0_3 "$(F0_3_OBS)") \
          $(if $(JUNIT),--check-cases F1_1 "$(F1_1_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F1_2 "$(F1_2_CASES)" "$(JUNIT)") \
          $(if $(S4_OBS),--check-attempt F1_1 "$(S4_OBS)") \
          $(if $(S6_OBS),--check-attempt F1_3 "$(S6_OBS)") \
          $(if $(JUNIT),--check-cases F2_1 "$(F2_1_CASES)" "$(JUNIT)") \
          $(if $(SEED_PRS_OBS),--check-seed-prs F2_1 "$(SEED_PRS_OBS)") \
          $(if $(BYPASS_OBS),--check-bypass F2_1 "$(BYPASS_OBS)") \
          $(if $(DOORS_OBS),--check-doors F2_2 "$(DOORS_OBS)") \
          $(if $(JUNIT),--check-cases F3_1 "$(F3_1_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F3_2 "$(F3_2_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F3_3 "$(F3_3_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F3_6 "$(F3_6_CASES)" "$(JUNIT)") \
          $(if $(INGEST_OBS),--check-ingest F3_5 "$(INGEST_OBS)") \
          $(if $(JUNIT),--check-cases F4_1 "$(F4_1_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F4_2 "$(F4_2_CASES)" "$(JUNIT)") \
          $(if $(and $(JUNIT),$(A_VS_A)),--check-cases F4_3 "$(F4_3_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F4_4 "$(F4_4_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F5_1 "$(F5_1_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F6_1 "$(F6_1_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F6_4 "$(F6_4_CASES)" "$(JUNIT)") \
          $(if $(RUN_URL),--run-url "$(RUN_URL)")
# CI passes a file path; the gate's exit code is written there, so a REJECTED
# envelope (exit 2) is told from a RED one and is not recorded (M01 item 9).
GATE_EXIT ?=

# $(1) folder, $(2) file stem, $(3) extra flags for verdict.build
# A runner exits 1 when a call failed. It has still written what it saw,
# so the chain goes on (the leading `-`) and build writes UNMEASURED. If it
# wrote nothing, the next line fails on the missing file.
#
# A_VS_A (M04 PR 2, SPEC/04 §4): each subject runs a second time on the same
# tree, into `-b` raws that build compares with the first. Neither is
# committed; the ids that differ are in the envelope's `a_vs_a`.
#
# The control's second run goes first, and outside the tree. src/baseline/
# is frozen, and its runner calls any untracked file dirty (the agent's
# runner leaves evals/history/ out), so run after the first raw was written
# it recorded a dirty tree and build refused the pair: PR 2's first labelled
# run, 36345059724. Its raw is moved in once the first run has written.
A_VS_A_TMP := $(or $(RUNNER_TEMP),$(TMPDIR),/tmp)
A_VS_A_RUNS = $(if $(A_VS_A),--raw $(1)/$(2).baseline-raw-b.json --raw $(1)/$(2).agent-raw-b.json)
A_VS_A_FLAGS = $(if $(A_VS_A),--a-vs-a $(1)/$(2).agent-raw-b.json --a-vs-a-control $(1)/$(2).baseline-raw-b.json)
ifneq ($(AGENT_RUNNER),)
define chain
	$(if $(A_VS_A),-uv run python -m src.baseline.run --out $(A_VS_A_TMP)/$(2).baseline-raw-b.json)
	-uv run python -m src.baseline.run --out $(1)/$(2).baseline-raw.json
	$(if $(A_VS_A),mv $(A_VS_A_TMP)/$(2).baseline-raw-b.json $(1)/$(2).baseline-raw-b.json)
	uv run python -m src.verdict.build card --raw $(1)/$(2).baseline-raw.json --out $(1)/$(2).baseline-card.json $(3)
	-uv run python -m src.agent.run --out $(1)/$(2).agent-raw.json --recheck-runtime
	$(if $(A_VS_A),-uv run python -m src.agent.run --out $(1)/$(2).agent-raw-b.json --recheck-runtime)
	uv run python -m src.cost_cap --raw $(1)/$(2).baseline-raw.json --raw $(1)/$(2).agent-raw.json $(A_VS_A_RUNS)
	$(if $(SWAPS_OBS),uv run python scripts/rule_swaps.py "$(SWAPS_OBS)" --out "$(SWAPS_RULED)")
	uv run python -m src.verdict.build envelope --raw $(1)/$(2).agent-raw.json --control-card $(1)/$(2).baseline-card.json --out $(1)/$(2).json $(3) $(CHECKS) $(A_VS_A_FLAGS) $(if $(SWAPS_OBS),--swaps "$(SWAPS_RULED)") $(if $(CONTAINMENT_OBS),--containment "$(CONTAINMENT_OBS)") $(if $(TEMPLATE_OBS),--template "$(TEMPLATE_OBS)")
	uv run python -m src.verdict.gate $(1)/$(2).json; code=$$?; $(if $(GATE_EXIT),echo $$code > "$(GATE_EXIT)";) exit $$code
endef
else
define chain
	-uv run python -m src.baseline.run --out $(1)/$(2).baseline-raw.json
	uv run python -m src.verdict.build card --raw $(1)/$(2).baseline-raw.json --out $(1)/$(2).baseline-card.json $(3)
	uv run python -m src.cost_cap --raw $(1)/$(2).baseline-raw.json
	uv run python -m src.verdict.build envelope --raw $(1)/$(2).baseline-raw.json --control-card $(1)/$(2).baseline-card.json --out $(1)/$(2).json $(3) $(CHECKS)
	uv run python -m src.verdict.gate $(1)/$(2).json; code=$$?; $(if $(GATE_EXIT),echo $$code > "$(GATE_EXIT)";) exit $$code
endef
endif

# CI only: it writes evals/history/, and only CI-written envelopes are
# evidence (P11, ADR-0003). verdict.build refuses it unless GITHUB_ACTIONS
# is "true"; the first line says so before any tokens are spent. That is an
# environment variable, not a proof of who ran it.
evals:
	@uv run python -c "import os, sys; sys.exit(0 if os.environ.get('GITHUB_ACTIONS') == 'true' else 'make evals writes evals/history/, which is CI-written only. Use make evals-local.')"
	$(call chain,$(HISTORY),$(COMMIT),)

# Your credentials, your cost. Writes evals/local/ only. Not evidence (P11).
evals-local:
	$(call chain,$(LOCAL),$(COMMIT),--allow-dirty)

validate:
	uv run python -m src.validate

plants:
	@uv run python -m src.verdict.gate --plants

ledger:
	@uv run python -m src.ledger

# Writes docs/milestones/README.md from the ledger. Never hand-edit that file.
ledger-plain:
	@uv run python -m src.ledger --plain
