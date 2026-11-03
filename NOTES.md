# Notes

## Assumptions

- Suppress records are normalized and matched like mail records but never appear in the output
  sheets. One that fails validation suppresses nobody.
- `Mail` echoes name and address exactly as input; only `ZIP5` is normalized.
- `SURVIVOR_REC_ID` is blank for `REJECT` and `SUPPRESS`, since neither has a survivor.
- Rejected records take no part in matching, so they never count toward `MULTI_COUNT`.
- KEY_CODE, TYPE and LIST are trimmed, so a stray space cannot detach a record from its file.

## Where these rules go wrong

**1. An initial matches every name with that letter.** At 3 River Rd, 37201, `100141 J Smith`
matches both `100064 John Smith` and `100003 Jane Smith`, so transitivity merges John and Jane and
Jane loses her letter. Suppression shares the weakness: `100024 E Moore` correctly removes
`100025 Elizabeth` and `100103 Liz Moore` at 6 Bay Rd, but would equally remove an Edward Moore
living there.
*Change:* accept an initial only when it fits a single full name in the group, and never for
suppression, where a wrong match is a compliance problem rather than a wasted stamp.

**2. A blank suffix matches a filled one.** `100007 Daniel Price` and `100026 Daniel Price JR` at
42 Quarry Rd are merged, so Daniel Jr. loses his letter to, most likely, his father. The rules
already treat JR and SR as different people; making blank a wildcard throws that away exactly where
it matters, at a shared family address.
*Change:* once any record in a group carries a generational suffix, treat blank as its own value,
or flag the group for review.

**3. The nickname table is one-way.** `100154 Chris Lowe` and `100108 Christina Lowe` at 305 Glen
Way stay apart because CHRIS maps only to CHRISTOPHER, while `100125 Bill` and `100133 Will Turner`
merge although they may well be two people.
*Change:* store equivalence classes (CHRIS with both CHRISTOPHER and CHRISTINA) and treat a
nickname-only match as weaker evidence that needs a second signal.

## How I would test it

The tests mirror the stages of the program: `test_normalize.py` covers each field rule and the
invalid shapes around it, `test_matching.py` has one test per matching rule plus transitivity,
`test_resolve.py` covers each group outcome (suppress, intra/inter, tie-break, distinct-list
`MULTI_COUNT`), `test_read_input.py` checks spreadsheet quirks (numeric ZIPs, stray spaces), and
`test_end_to_end.py` runs four records through the whole pipeline. The Summary balance identity is
enforced in the program, so it holds on any input. On real data I would also pin the counts for a
known file and diff `Drops` between runs: the real risk in merge/purge is not a crash but a quiet
change in who gets suppressed.
