# Engineering. All five targets exist from M00 PR 1 (SPEC/00 §8 M00).
# evals, plants and ledger run from M00 PR 2.

.PHONY: evals evals-local validate plants ledger

# Your credentials, your cost. Writes evals/local/ only. Not evidence (P11).
# At PR 1 this writes raw observations, not an envelope: src/verdict/ is PR 2.
evals-local:
	uv run python -m src.baseline.run --out evals/local/m00-pr1-baseline.json

validate:
	uv run python -m src.validate

# The recipe exits 1. GNU make then exits 2, as it does for any failed recipe.
evals plants ledger:
	@echo not until M00 PR 2 && exit 1
