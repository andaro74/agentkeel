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
CHECKS := $(if $(F0_2_JUNIT),--check-junit F0_2 tests.test_f0_2 "$(F0_2_JUNIT)") \
          $(if $(F0_3_OBS),--check-pr F0_3 "$(F0_3_OBS)") \
          $(if $(JUNIT),--check-cases F1_1 "$(F1_1_CASES)" "$(JUNIT)") \
          $(if $(JUNIT),--check-cases F1_2 "$(F1_2_CASES)" "$(JUNIT)") \
          $(if $(S4_OBS),--check-attempt F1_1 "$(S4_OBS)") \
          $(if $(S6_OBS),--check-attempt F1_3 "$(S6_OBS)") \
          $(if $(RUN_URL),--run-url "$(RUN_URL)")
# CI passes a file path; the gate's exit code is written there, so a REJECTED
# envelope (exit 2) is told from a RED one and is not recorded (M01 item 9).
GATE_EXIT ?=

# $(1) folder, $(2) file stem, $(3) extra flags for verdict.build
# A runner exits 1 when a call failed. It has still written what it saw,
# so the chain goes on (the leading `-`) and build writes UNMEASURED. If it
# wrote nothing, the next line fails on the missing file.
ifneq ($(AGENT_RUNNER),)
define chain
	-uv run python -m src.baseline.run --out $(1)/$(2).baseline-raw.json
	uv run python -m src.verdict.build card --raw $(1)/$(2).baseline-raw.json --out $(1)/$(2).baseline-card.json $(3)
	-uv run python -m src.agent.run --out $(1)/$(2).agent-raw.json
	uv run python -m src.cost_cap --raw $(1)/$(2).baseline-raw.json --raw $(1)/$(2).agent-raw.json
	uv run python -m src.verdict.build envelope --raw $(1)/$(2).agent-raw.json --control-card $(1)/$(2).baseline-card.json --out $(1)/$(2).json $(3) $(CHECKS)
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
