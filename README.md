# Mailing List Merge/Purge

Reads a campaign workbook and decides who gets a letter: one letter per person, suppressed
people removed, and for every person kept the list that "owns" them.

## Install

Python 3.9+ and one dependency, `openpyxl`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python merge.py merge_test_input.xlsx output.xlsx
```

On `merge_test_input.xlsx` this prints `132 mailed, 24 dropped -> output.xlsx`: 156 mail records in,
3 rejected, 3 suppressed, 18 dropped as duplicates, 9 of the survivors found on two or more
rented lists.

`output.xlsx` is written with three sheets:

| Sheet | Contents |
| --- | --- |
| `Mail` | one row per surviving mail record, with its `MULTI_COUNT` |
| `Drops` | one row per removed mail record, with the reason and the surviving `REC_ID` |
| `Summary` | per input file, then a `TOTAL` row; every row balances `INPUT = REJECT + SUPPRESS + DUP_INTER + DUP_INTRA + NET` |

## Tests

```bash
python -m unittest discover
```

## Layout

| File | Contents |
| --- | --- |
| `normalize.py` | field normalization and record validation |
| `matching.py` | when two records are the same person, and transitive grouping |
| `merge.py` | reading the workbook, what happens to each group, and the output |

`NOTES.md` has the assumptions and where these rules would go wrong on real data.
