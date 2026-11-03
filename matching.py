"""Deciding who is the same person, and grouping them."""

from collections import defaultdict


def block_key(record):
    """Rules 1 and 2 are exact equality, so only records sharing this key can match."""
    return (record.zip5, record.house, record.street, record.unit, record.last)


def same_person(a, b, nicknames):
    if a.suffix and b.suffix and a.suffix != b.suffix:
        return False
    if not a.first or not b.first:
        return False
    initial = (len(a.first) == 1 and a.first == b.first[0]) or (
        len(b.first) == 1 and b.first == a.first[0]
    )
    return initial or nicknames.get(a.first, a.first) == nicknames.get(b.first, b.first)


def group(records, nicknames):
    """Transitive groups: A~B and B~C puts A, B and C together."""
    parent = {record.rec_id: record.rec_id for record in records}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    blocks = defaultdict(list)
    for record in records:
        blocks[block_key(record)].append(record)

    for members in blocks.values():
        for i, a in enumerate(members):
            for b in members[i + 1:]:
                if same_person(a, b, nicknames):
                    parent[find(a.rec_id)] = find(b.rec_id)

    groups = defaultdict(list)
    for record in records:
        groups[find(record.rec_id)].append(record)
    return list(groups.values())
