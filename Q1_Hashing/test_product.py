import unittest
from datetime import date

from product import Product, Medicine, HealthSupplement
from hash_table import HashTable


def make_medicine(**changes):
    data = dict(product_id="P1042", name="Paracetamol 500mg", price=5.9,
                stock_quantity=120, manufacturer="Panadol Co.",
                expiry_date="2027-12-31", dosage="500mg tablet",
                requires_prescription=False)
    data.update(changes)
    return Medicine(**data)


class TestProduct(unittest.TestCase):

    def test_create_medicine(self):
        m = make_medicine()
        self.assertEqual(m.product_id, "P1042")
        self.assertEqual(m.price, 5.90)
        self.assertEqual(m.expiry_date, date(2027, 12, 31))   # text converted to date
        self.assertEqual(m.product_type(), "Medicine")

    def test_create_supplement(self):
        s = HealthSupplement("S2001", "Vitamin C 1000mg", 32.5, 40, "Blackmores",
                             date(2028, 6, 30), "Vitamin", 60)
        self.assertEqual(s.product_type(), "Health Supplement")
        self.assertIn(("Servings/Pack", 60), s.extra_details())

    def test_product_id_normalised(self):
        self.assertEqual(make_medicine(product_id="  p1042 ").product_id, "P1042")

    def test_invalid_values_rejected(self):
        with self.assertRaises(ValueError):
            make_medicine(price=-1)
        with self.assertRaises(ValueError):
            make_medicine(stock_quantity=-5)
        with self.assertRaises(ValueError):
            make_medicine(name="   ")
        with self.assertRaises(ValueError):
            make_medicine(expiry_date="31/12/2027")      # wrong format
        with self.assertRaises(ValueError):
            make_medicine(price="abc")                   # not a number

    def test_base_class_cannot_be_created(self):
        with self.assertRaises(TypeError):               # abstract class
            Product("X1", "x", 1, 1, "m", date.today())

    def test_expiry_check(self):
        m = make_medicine(expiry_date="2026-01-01")
        self.assertTrue(m.is_expired(today=date(2026, 11, 3)))
        self.assertFalse(m.is_expired(today=date(2025, 1, 1)))

    def test_summary_format(self):
        self.assertEqual(make_medicine().summary(),
                         "ID: P1042 | Name: Paracetamol 500mg | Price: RM5.90 | Stock: 120")

    def test_store_in_hash_table(self):
        table = HashTable()
        m = make_medicine()
        table.insert(m.product_id, m)                    # key = ID, value = object
        self.assertIs(table.search("P1042"), m)


if __name__ == "__main__":
    unittest.main()