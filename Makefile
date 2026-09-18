# Engineering. All five targets exist from M00 PR 1 and run from M00 PR 2
# (SPEC/00 §8 M00).
#
# The chain is the same in CI and locally (P5): the runner writes raw
# observations, cost-cap reads the spend, verdict.build writes the card and
# the envelope, verdict.gate rules on the envelope. A recipe that fails
# exits 1 (gate: 1 RED, 2 REJECTED; build: 3 REFUSED); GNU make then exits 2.

.PHONY: evals evals-local validate plants ledger --plain

COMMIT := $(shell git rev-parse HEAD)
HISTORY := evals/history
LOCAL := evals/local

# CI passes these. Each becomes an entry in the envelope's `checks`.
F0_2_JUNIT ?=
F0_3_OBS ?=
RUN_URL ?=
CHECKS := $(if $(F0_2_JUNIT),--check-junit F0_2 tests.test_f0_2 "$(F0_2_JUNIT)") \
          $(if $(F0_3_OBS),--check-pr F0_3 "$(F0_3_OBS)") \
          $(if $(RUN_URL),--run-url "$(RUN_URL)")

# $(1) folder, $(2) file stem, $(3) extra flags for verdict.build
# The runner exits 1 when a call failed. It has still written what it saw,
# so the chain goes on (the leading `-`) and build writes UNMEASURED. If it
# wrote nothing, the next line fails on the missing file.
define chain
	-uv run python -m src.baseline.run --out $(1)/$(2).baseline-raw.json
	uv run python -m src.cost_cap --raw $(1)/$(2).baseline-raw.json
	uv run python -m src.verdict.build card --raw $(1)/$(2).baseline-raw.json --out $(1)/$(2).baseline-card.json $(3)
	uv run python -m src.verdict.build envelope --raw $(1)/$(2).baseline-raw.json --baseline-card $(1)/$(2).baseline-card.json --out $(1)/$(2).json $(3) $(CHECKS)
	uv run python -m src.verdict.gate $(1)/$(2).json
endef

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

# GNU make takes `--plain` for an option of its own and stops. Write
# `make ledger -- --plain` or `make ledger PLAIN=1`.
ledger:
	@uv run python -m src.ledger $(if $(or $(PLAIN),$(filter --plain,$(MAKECMDGOALS))),--plain)

--plain:
	@:
