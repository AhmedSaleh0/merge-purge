"""Mailing list merge/purge: one letter per person.

Usage: python merge.py merge_test_input.xlsx output.xlsx
"""

import sys
from dataclasses import dataclass

from openpyxl import Workbook, load_workbook

import matching
import normalize

MAIL_COLUMNS = [
    "REC_ID", "KEY_CODE", "FIRST_NAME", "LAST_NAME", "SUFFIX",
    "ADDRESS_1", "ADDRESS_2", "CITY", "STATE", "ZIP5", "MULTI_COUNT",
]
DROP_COLUMNS = ["REC_ID", "KEY_CODE", "REASON", "SURVIVOR_REC_ID"]
SUMMARY_COLUMNS = [
    "KEY_CODE", "INPUT", "REJECT", "SUPPRESS", "DUP_INTER", "DUP_INTRA", "NET", "MULTIS",
]


@dataclass
class File:
    key_code: str
    type: str
    priority: int
    list_name: str


# --- input ---------------------------------------------------------------

def cell(value):
    """Spreadsheet cell as text, keeping names and addresses exactly as entered."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def read_sheet(workbook, name):
    rows = workbook[name].iter_rows(values_only=True)
    header = [cell(h).strip() for h in next(rows)]
    return [dict(zip(header, map(cell, row))) for row in rows if any(v is not None for v in row)]


def read_input(path):
    workbook = load_workbook(path, data_only=True)
    plan = {
        row["KEY_CODE"]: File(
            key_code=row["KEY_CODE"],
            type=row["TYPE"],
            priority=int(row["PRIORITY"]) if row["PRIORITY"] else 0,
            list_name=row["LIST"],
        )
        for row in read_sheet(workbook, "Plan")
    }
    nicknames = {r["NICKNAME"].upper(): r["FULL_NAME"].upper()
                 for r in read_sheet(workbook, "Nicknames")}
    suffixes = {r["WORD"].upper(): r["STANDARD"].upper()
                for r in read_sheet(workbook, "StreetSuffixes")}
    records = [normalize.build(row, suffixes) for row in read_sheet(workbook, "Records")]
    return plan, nicknames, records


# --- what happens to each group -------------------------------------------

def multi_count(survivor, mail, plan):
    """Distinct Outside lists the person was found on; 0 for a House survivor."""
    if plan[survivor.key_code].type != "Outside":
        return 0
    return len({plan[r.key_code].list_name for r in mail if plan[r.key_code].type == "Outside"})


def resolve(groups, plan):
    survivors, drops = [], []
    for members in groups:
        mail = [r for r in members if plan[r.key_code].type != "Suppress"]
        if not mail:
            continue
        if any(plan[r.key_code].type == "Suppress" for r in members):
            drops += [(r, "SUPPRESS", "") for r in mail]
            continue
        survivor = min(mail, key=lambda r: (plan[r.key_code].priority, r.rec_id))
        for r in mail:
            if r is not survivor:
                reason = "DUP_INTRA" if r.key_code == survivor.key_code else "DUP_INTER"
                drops.append((r, reason, survivor.rec_id))
        survivors.append((survivor, multi_count(survivor, mail, plan)))
    return survivors, drops


def run(plan, nicknames, records):
    mail_records = [r for r in records if plan[r.key_code].type != "Suppress"]
    drops = [(r, "REJECT", "") for r in mail_records if not r.valid]
    matchable = [r for r in records if r.valid]
    survivors, duplicate_drops = resolve(matching.group(matchable, nicknames), plan)
    return survivors, drops + duplicate_drops


# --- output --------------------------------------------------------------

def mail_rows(survivors):
    rows = []
    for record, count in survivors:
        raw = record.raw
        rows.append([
            record.rec_id, record.key_code, raw["FIRST_NAME"], raw["LAST_NAME"], raw["SUFFIX"],
            raw["ADDRESS_1"], raw["ADDRESS_2"], raw["CITY"], raw["STATE"], record.zip5, count,
        ])
    return sorted(rows)


def drop_rows(drops):
    return sorted([record.rec_id, record.key_code, reason, survivor_id]
                  for record, reason, survivor_id in drops)


def summary_rows(plan, records, survivors, drops):
    reasons = {record.rec_id: reason for record, reason, _ in drops}
    counts = {record.rec_id: count for record, count in survivors}
    rows = []
    for key_code, file in plan.items():
        if file.type == "Suppress":
            continue
        mine = [r for r in records if r.key_code == key_code]
        row = [key_code, len(mine)]
        for reason in ("REJECT", "SUPPRESS", "DUP_INTER", "DUP_INTRA"):
            row.append(sum(1 for r in mine if reasons.get(r.rec_id) == reason))
        kept = [r for r in mine if r.rec_id in counts]
        row.append(len(kept))
        row.append(sum(1 for r in kept if counts[r.rec_id] >= 2))
        rows.append(row)
    total = ["TOTAL"] + [sum(row[i] for row in rows) for i in range(1, len(SUMMARY_COLUMNS))]
    rows.append(total)
    for row in rows:
        if row[1] != sum(row[2:7]):
            raise ValueError(f"summary does not balance: {row}")
    return rows


def write_output(path, sheets):
    workbook = Workbook()
    workbook.remove(workbook.active)
    for name, (columns, rows) in sheets.items():
        sheet = workbook.create_sheet(name)
        sheet.append(columns)
        for row in rows:
            sheet.append(row)
    workbook.save(path)


def main(argv):
    if len(argv) != 3:
        print(f"usage: python {argv[0] or 'merge.py'} <input.xlsx> <output.xlsx>", file=sys.stderr)
        return 2
    plan, nicknames, records = read_input(argv[1])
    survivors, drops = run(plan, nicknames, records)
    write_output(argv[2], {
        "Mail": (MAIL_COLUMNS, mail_rows(survivors)),
        "Drops": (DROP_COLUMNS, drop_rows(drops)),
        "Summary": (SUMMARY_COLUMNS, summary_rows(plan, records, survivors, drops)),
    })
    print(f"{len(survivors)} mailed, {len(drops)} dropped -> {argv[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
