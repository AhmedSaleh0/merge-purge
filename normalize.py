"""Field normalization and record validation."""

import re
from dataclasses import dataclass

UNIT_WORDS = {"APT", "APARTMENT", "UNIT", "STE", "SUITE"}


def name(value):
    """Upper case, keep only A-Z: "  michael " -> MICHAEL, "o'brien" -> OBRIEN."""
    return re.sub(r"[^A-Z]", "", value.upper())


def zip5(value):
    """Part before "-", left-padded to 5 digits. None when invalid."""
    head = value.split("-")[0].strip()
    return head.zfill(5) if re.fullmatch(r"[0-9]{3,5}", head) else None


def address1(value, street_suffixes):
    """(house number, street) or None when there is no numeric house number."""
    tokens = value.upper().replace(".", " ").replace(",", " ").split()
    if not tokens or not re.fullmatch(r"[0-9]+", tokens[0]):
        return None
    house, street = tokens[0], tokens[1:]
    if street:
        street[-1] = street_suffixes.get(street[-1], street[-1])
    return house, " ".join(street)


def unit(value):
    """Apt. 12b -> 12B, #12B -> 12B, "" -> ""."""
    text = value.upper().replace(".", "").replace(",", "").replace("#", "")
    return "".join(word for word in text.split() if word not in UNIT_WORDS)


@dataclass
class Record:
    rec_id: int
    key_code: str
    raw: dict
    first: str
    last: str
    suffix: str
    zip5: str
    house: str
    street: str
    unit: str
    valid: bool


def build(row, street_suffixes):
    address = address1(row["ADDRESS_1"], street_suffixes)
    code = zip5(row["ZIP"])
    last = name(row["LAST_NAME"])
    house, street = address if address else ("", "")
    return Record(
        rec_id=int(row["REC_ID"]),
        key_code=row["KEY_CODE"].strip(),
        raw=row,
        first=name(row["FIRST_NAME"]),
        last=last,
        suffix=name(row["SUFFIX"]),
        zip5=code or "",
        house=house,
        street=street,
        unit=unit(row["ADDRESS_2"]),
        valid=bool(last) and code is not None and address is not None,
    )
