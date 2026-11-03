"""Survivor, drop reason and MULTI_COUNT for each group."""

import unittest

import merge
import normalize

PLAN = {
    "H01": merge.File("H01", "House", 10, "Customers"),
    "O01": merge.File("O01", "Outside", 50, "Alpha"),
    "O02": merge.File("O02", "Outside", 50, "Alpha"),
    "O03": merge.File("O03", "Outside", 60, "Gamma"),
    "S01": merge.File("S01", "Suppress", 0, "Do Not Mail"),
}


def record(rec_id, key_code, first, last="King", zip_code="30301"):
    return normalize.build({
        "REC_ID": rec_id, "KEY_CODE": key_code, "FIRST_NAME": first, "LAST_NAME": last,
        "SUFFIX": "", "ADDRESS_1": "14 Maple St", "ADDRESS_2": "", "ZIP": zip_code,
    }, {"ST": "ST"})


def run(*records):
    survivors, drops = merge.run(PLAN, {}, list(records))
    return ({r.rec_id: count for r, count in survivors},
            {r.rec_id: (reason, survivor) for r, reason, survivor in drops})


class TestResolve(unittest.TestCase):
    def test_a_suppress_record_removes_every_mail_record_in_its_group(self):
        mail, drops = run(record(1, "H01", "Ann"), record(2, "O01", "Ann"), record(3, "S01", "Ann"))
        self.assertEqual(mail, {})
        self.assertEqual(drops, {1: ("SUPPRESS", ""), 2: ("SUPPRESS", "")})

    def test_a_suppress_record_also_links_people_who_do_not_match_directly(self):
        mail, drops = run(record(1, "O01", "John"), record(2, "S01", "J"), record(3, "O03", "Jane"))
        self.assertEqual(mail, {})
        self.assertEqual(set(drops), {1, 3})

    def test_an_invalid_suppress_record_suppresses_nobody(self):
        mail, drops = run(record(1, "O01", "Ann"), record(2, "S01", "Ann", zip_code="N/A"))
        self.assertEqual(mail, {1: 1})
        self.assertEqual(drops, {})

    def test_a_duplicate_from_the_survivors_own_file_is_intra(self):
        mail, drops = run(record(1, "O03", "Ann"), record(2, "O03", "Ann"))
        self.assertEqual(drops, {2: ("DUP_INTRA", 1)})

    def test_equal_priority_is_decided_by_the_lowest_rec_id(self):
        mail, drops = run(record(9, "O01", "Ann"), record(4, "O02", "Ann"))
        self.assertIn(4, mail)
        self.assertEqual(drops, {9: ("DUP_INTER", 4)})

    def test_multi_count_counts_distinct_lists_not_files(self):
        mail, _ = run(record(1, "O01", "Ann"), record(2, "O02", "Ann"), record(3, "O03", "Ann"))
        self.assertEqual(mail, {1: 2})

    def test_a_rejected_record_takes_no_part_in_matching(self):
        mail, drops = run(record(1, "O01", "Ann"), record(2, "O03", "Ann", last=""))
        self.assertEqual(mail, {1: 1})
        self.assertEqual(drops, {2: ("REJECT", "")})


if __name__ == "__main__":
    unittest.main()
