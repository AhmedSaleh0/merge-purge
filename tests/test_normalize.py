import unittest

import normalize

SUFFIXES = {"STREET": "ST", "ST": "ST", "DRIVE": "DR", "DR": "DR", "WAY": "WAY"}


class TestNames(unittest.TestCase):
    def test_keeps_only_letters(self):
        self.assertEqual(normalize.name("  michael "), "MICHAEL")
        self.assertEqual(normalize.name("o'brien"), "OBRIEN")
        self.assertEqual(normalize.name("Smith-Jones"), "SMITHJONES")
        self.assertEqual(normalize.name("Jr."), "JR")
        self.assertEqual(normalize.name(""), "")


class TestZip(unittest.TestCase):
    def test_pads_and_trims_to_five_digits(self):
        self.assertEqual(normalize.zip5("2134"), "02134")
        self.assertEqual(normalize.zip5("02134-1102"), "02134")
        self.assertIsNone(normalize.zip5("N/A"))

    def test_invalid_shapes(self):
        self.assertIsNone(normalize.zip5("ABCDE"))
        self.assertIsNone(normalize.zip5(""))
        self.assertIsNone(normalize.zip5("12"))
        self.assertIsNone(normalize.zip5("123456"))


class TestAddress1(unittest.TestCase):
    def test_splits_house_number_and_standardises_street_type(self):
        self.assertEqual(normalize.address1("14 Maple Street", SUFFIXES), ("14", "MAPLE ST"))
        self.assertEqual(normalize.address1("101 Forest Dr.", SUFFIXES), ("101", "FOREST DR"))

    def test_only_the_last_token_is_standardised(self):
        self.assertEqual(normalize.address1("5 Way Street", SUFFIXES), ("5", "WAY ST"))

    def test_house_number_must_be_numeric(self):
        self.assertIsNone(normalize.address1("PO Box 12", SUFFIXES))
        self.assertIsNone(normalize.address1("", SUFFIXES))


class TestUnit(unittest.TestCase):
    def test_drops_unit_words_and_punctuation(self):
        self.assertEqual(normalize.unit("Apt. 12b"), "12B")
        self.assertEqual(normalize.unit("#12B"), "12B")
        self.assertEqual(normalize.unit(""), "")
        self.assertEqual(normalize.unit("Suite 200"), "200")


def record(**overrides):
    row = {
        "REC_ID": "1", "KEY_CODE": "H01", "FIRST_NAME": "Ann", "LAST_NAME": "King",
        "SUFFIX": "", "ADDRESS_1": "14 Maple Street", "ADDRESS_2": "", "ZIP": "30301",
    }
    row.update(overrides)
    return normalize.build(row, SUFFIXES)


class TestValidation(unittest.TestCase):
    def test_a_clean_record_is_valid(self):
        self.assertTrue(record().valid)

    def test_rejected_when_last_name_zip_or_house_number_is_missing(self):
        self.assertFalse(record(LAST_NAME=" ").valid)
        self.assertFalse(record(ZIP="N/A").valid)
        self.assertFalse(record(ADDRESS_1="Maple Street").valid)


if __name__ == "__main__":
    unittest.main()
