"""Spreadsheet quirks the rules depend on."""

import io
import unittest

from openpyxl import Workbook

import merge


def workbook(plan_key_code, record_key_code, zip_value):
    book = Workbook()
    book.remove(book.active)
    sheets = {
        "Plan": [["KEY_CODE", "TYPE", "PRIORITY", "LIST", "SEGMENT"],
                 [plan_key_code, "House ", 10, "Customers", "All"]],
        "Records": [["REC_ID", "KEY_CODE", "FIRST_NAME", "LAST_NAME", "SUFFIX", "ADDRESS_1",
                     "ADDRESS_2", "CITY", "STATE", "ZIP"],
                    [100001, record_key_code, "Ann", "King", None, "14 Maple St", None,
                     "Newark", "NJ", zip_value]],
        "Nicknames": [["NICKNAME", "FULL_NAME"]],
        "StreetSuffixes": [["WORD", "STANDARD"], ["ST", "ST"]],
    }
    for name, rows in sheets.items():
        sheet = book.create_sheet(name)
        for row in rows:
            sheet.append(row)
    buffer = io.BytesIO()
    book.save(buffer)
    buffer.seek(0)
    return buffer


class TestReadInput(unittest.TestCase):
    def test_a_numeric_zip_gets_its_leading_zero_back(self):
        plan, nicknames, records = merge.read_input(workbook("H01", "H01", 7102))
        self.assertEqual(records[0].zip5, "07102")
        self.assertTrue(records[0].valid)

    def test_stray_spaces_in_key_code_and_type_do_not_break_the_link(self):
        plan, nicknames, records = merge.read_input(workbook(" H01", "H01 ", "07102"))
        survivors, drops = merge.run(plan, nicknames, records)
        self.assertEqual([(r.rec_id, r.key_code, count) for r, count in survivors],
                         [(100001, "H01", 0)])


if __name__ == "__main__":
    unittest.main()
