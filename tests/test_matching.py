import unittest

import matching
import normalize

NICKNAMES = {"BOB": "ROBERT", "ROB": "ROBERT", "BILL": "WILLIAM", "WILL": "WILLIAM"}
SUFFIXES = {"STREET": "ST", "ST": "ST"}


def record(rec_id, first, last="King", suffix="", address="14 Maple Street",
           unit="", zip_code="30301", key_code="H01"):
    return normalize.build({
        "REC_ID": rec_id, "KEY_CODE": key_code, "FIRST_NAME": first, "LAST_NAME": last,
        "SUFFIX": suffix, "ADDRESS_1": address, "ADDRESS_2": unit, "ZIP": zip_code,
    }, SUFFIXES)


def same(a, b):
    return matching.same_person(a, b, NICKNAMES)


class TestSamePerson(unittest.TestCase):
    def test_nicknames_resolve_to_the_same_person(self):
        self.assertTrue(same(record(1, "Robert"), record(2, "bob")))
        self.assertTrue(same(record(1, "Bill"), record(2, "Will")))

    def test_an_initial_matches_the_full_name(self):
        self.assertTrue(same(record(1, "J"), record(2, "John")))
        self.assertTrue(same(record(1, "R."), record(2, "Robert")))

    def test_an_initial_does_not_match_a_different_nickname(self):
        self.assertFalse(same(record(1, "R"), record(2, "bob")))

    def test_different_first_names_are_different_people(self):
        self.assertFalse(same(record(1, "Mary"), record(2, "Robert")))

    def test_an_empty_first_name_never_matches(self):
        self.assertFalse(same(record(1, ""), record(2, "")))

    def test_two_filled_suffixes_must_agree(self):
        self.assertFalse(same(record(1, "Tom", suffix="Jr"), record(2, "Tom", suffix="Sr")))
        self.assertTrue(same(record(1, "Tom", suffix="Jr"), record(2, "Tom")))

    def test_last_name_zip_address_and_unit_must_match(self):
        self.assertNotEqual(matching.block_key(record(1, "Ann")),
                            matching.block_key(record(2, "Ann", last="Queen")))
        self.assertNotEqual(matching.block_key(record(1, "Ann")),
                            matching.block_key(record(2, "Ann", zip_code="30302")))
        self.assertNotEqual(matching.block_key(record(1, "Ann")),
                            matching.block_key(record(2, "Ann", unit="Apt 2")))

    def test_an_empty_unit_equals_an_empty_unit_only(self):
        self.assertEqual(matching.block_key(record(1, "Ann")),
                         matching.block_key(record(2, "Ann", address="14 Maple St")))


class TestGrouping(unittest.TestCase):
    def test_matches_are_transitive(self):
        records = [record(1, "Robert"), record(2, "bob"), record(3, "R.")]
        groups = matching.group(records, NICKNAMES)
        self.assertEqual([sorted(r.rec_id for r in g) for g in groups], [[1, 2, 3]])

    def test_a_record_that_matches_nothing_is_its_own_group(self):
        groups = matching.group([record(1, "Robert"), record(2, "Mary")], NICKNAMES)
        self.assertEqual(sorted(len(g) for g in groups), [1, 1])


if __name__ == "__main__":
    unittest.main()
