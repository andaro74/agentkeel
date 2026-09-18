# tests/fixtures

`hand_written_envelope_no_baseline_card_ref.json` is M00's second seed: a
run without a baseline card. It was typed by hand from the numbers of the
PR 1 plant run (`22b5499`, feasibility.md §6.2). It has every envelope
field except `baseline_card_ref`, and it says GREEN.

Edited once, by hand, at ADR-0004: each result gained `scope: control`
when the schema began to require it. Without that the file would be
rejected for two reasons, and the test needs it rejected for one.

It is a false state, not evidence. It was committed before
`src/verdict/` existed, with the test that expects the gate to reject it.
Do not copy it to `evals/history/`. Do not add the missing field here;
`tests/test_f0_2.py` adds it in memory to show the file is rejected for
that reason and no other.
