"""Four records at one address, run through the whole pipeline."""

import unittest

import merge
import normalize

SUFFIXES = {"STREET": "ST", "ST": "ST"}
NICKNAMES = {"BOB": "ROBERT"}
PLAN = {
    "H1": merge.File("H1", "House", 10, "Customers"),
    "R1": merge.File("R1", "Outside", 50, "Alpha"),
    "R2": merge.File("R2", "Outside", 50, "Beta"),
}
ROWS = [
    ("11", "H1", "Robert", "King", "14 Maple Street", "30301"),
    ("12", "R1", "bob", "KING", "14 MAPLE ST.", "30301-4410"),
    ("13", "R2", "R.", "King", "14 Maple St", "30301"),
    ("14", "R2", "Mary", "King", "14 Maple St", "30301"),
]


class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        records = [normalize.build({
            "REC_ID": rec_id, "KEY_CODE": key_code, "FIRST_NAME": first, "LAST_NAME": last,
            "SUFFIX": "", "ADDRESS_1": address, "ADDRESS_2": "", "ZIP": zip_code,
        }, SUFFIXES) for rec_id, key_code, first, last, address, zip_code in ROWS]
        self.survivors, self.drops = merge.run(PLAN, NICKNAMES, records)

    def test_robert_survives_and_bob_and_r_are_dropped(self):
        self.assertEqual(sorted((r.rec_id, reason, survivor) for r, reason, survivor in self.drops),
                         [(12, "DUP_INTER", 11), (13, "DUP_INTER", 11)])

    def test_mary_matches_nobody_and_survives_on_her_own(self):
        self.assertEqual({r.rec_id: count for r, count in self.survivors}, {11: 0, 14: 1})


if __name__ == "__main__":
    unittest.main()
