"""Unit tests for InventoryService and array_search. Run with:
python -m unittest test_inventory_system -v"""

import unittest

from inventory_system import InventoryService
from hash_table import DuplicateKeyError
from array_search import linear_search
from sample_data import create_sample_products
from product import Medicine


class TestInventoryService(unittest.TestCase):

    def setUp(self):
        self.service = InventoryService()
        self.service.load(create_sample_products())

    def test_sample_data_loaded_into_both_structures(self):
        self.assertEqual(len(self.service.table), 10)
        self.assertEqual(len(self.service.array), 10)

    def test_search_finds_same_record_in_both(self):
        result = self.service.search("S2002")
        self.assertEqual(result["product"].name, "Fish Oil Omega-3")
        self.assertIs(self.service.array[result["index"]], result["product"])

    def test_search_missing(self):
        result = self.service.search("X999")
        self.assertIsNone(result["product"])
        self.assertEqual(result["comparisons"], 10)   # array checked every element

    def test_insert_adds_to_both(self):
        m = Medicine("P1042", "Aspirin 100mg", 4.5, 50, "Bayer", "2027-06-30", "100mg tablet")
        self.service.insert(m)
        self.assertIs(self.service.search("P1042")["product"], m)
        self.assertIn(m, self.service.array)

    def test_duplicate_insert_rejected(self):
        dup = Medicine("P1001", "Copy", 1, 1, "x", "2027-01-01", "x")
        with self.assertRaises(DuplicateKeyError):
            self.service.insert(dup)
        self.assertEqual(len(self.service.array), 10)  # array not changed either

    def test_delete_removes_from_both(self):
        self.service.delete("P1003")
        self.assertIsNone(self.service.search("P1003")["product"])
        self.assertEqual(len(self.service.array), 9)

    def test_linear_search_comparisons(self):
        array = self.service.array
        _, index, comparisons = linear_search(array, array[-1].product_id)
        self.assertEqual((index, comparisons), (9, 10))   # last element: n comparisons


if __name__ == "__main__":
    unittest.main()