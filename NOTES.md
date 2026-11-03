# Notes

## Assumptions

- Suppress records are normalized and matched like any other record, but they never appear in
  `Mail`, `Drops` or `Summary` — those sheets describe mail files only.
- A suppress record that fails validation is dropped silently and suppresses nobody.
- `Mail` carries the name and address exactly as they came in, including the stray case and spacing;
  only `ZIP5` is the normalized value.
- `SURVIVOR_REC_ID` is left blank for `REJECT` and `SUPPRESS`, since neither points at a survivor.
- A rejected record takes no part in matching, so it is also invisible to `MULTI_COUNT`.
- `Summary` lists the files in Plan order and asserts the balance identity on every row; a rule change
  that breaks it fails the run instead of shipping a wrong count.

## Where these rules would get it wrong

**1. A single initial matches every name that starts with that letter.** At 3 River Rd, 37201 the
input has `100064 John Smith`, `100141 J Smith` and `100003 Jane Smith`. `J` matches John and `J`
matches Jane, so transitivity folds all three into one group and Jane silently loses her letter even
though nothing ever claimed John and Jane are the same person. The same failure suppresses a whole
household: the do-not-mail record `100024 E Moore` at 6 Bay Rd kills both `100025 Elizabeth Moore`
and `100103 Liz Moore`, and would equally have killed an Edward Moore living there.
*Change:* an initial should only match when it is unambiguous inside the group — if the initial is
consistent with two different full names, keep the records apart. For a suppress record I would go
further and refuse initial-only matching outright: suppressing the wrong person is a compliance
problem, mailing them twice is a postage problem.

**2. A blank suffix matches a filled one, which merges father and son.** `100007 Daniel Price`
(no suffix) and `100026 Daniel Price JR` at 42 Quarry Rd, 78701 become one person, so Daniel senior
is dropped as a duplicate of his son. The rule already knows JR and SR are different people; treating
blank as a wildcard throws that away, and at a shared family address that is exactly where it matters.
*Change:* once any record in a group carries a generational suffix, treat blank as its own value
rather than a wildcard — or keep both and flag the group for review.

**3. The nickname table is one-way and uneven.** `100154 Chris Lowe` and `100108 Christina Lowe` at
305 Glen Way stay separate, because CHRIS maps to CHRISTOPHER and CHRISTINA maps to nothing — almost
certainly one woman getting two letters. Meanwhile `100125 Bill Turner` and `100133 Will Turner` are
merged, although Bill and Will at one address are as likely to be two people.
*Change:* make the table bidirectional equivalence classes rather than nickname → full name, and
treat a nickname-only match as weaker evidence than an exact or initial match, so it needs a second
signal before it merges.

## How I would test it

The rules split into three testable layers, and the tests follow that split: `tests/test_normalize.py`
runs each field rule against typical messy values plus the invalid shapes around
them, `tests/test_matching.py` checks one pair rule per test (nickname, initial, suffix conflict,
empty first name, the blocking fields) and that matching is transitive, and
`tests/test_end_to_end.py` runs four records through the pipeline and asserts the exact survivor, drop
reasons and `MULTI_COUNT`. Beyond that, the balance identity `INPUT = REJECT + SUPPRESS + DUP_INTER
+ DUP_INTRA + NET` is asserted inside the program rather than in a test, so it holds on any input.
On real data I would add a regression check that pins the counts for a known file and diffs the
`Drops` sheet between runs, because the risk with merge/purge is not a crash but a quiet change in
who gets suppressed.
