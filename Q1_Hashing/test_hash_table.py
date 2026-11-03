import unittest

from hash_table import HashTable, SlotState, DuplicateKeyError


def constant_hash(key, capacity):
    """Sends every key to slot 0 - forces collisions so probing can be tested."""
    return 0


class TestBasicOperations(unittest.TestCase):

    def setUp(self):
        self.table = HashTable(capacity=11)

    def test_insert_and_search(self):
        self.table.insert("P1001", "Paracetamol")
        self.assertEqual(self.table.search("P1001"), "Paracetamol")
        self.assertEqual(len(self.table), 1)

    def test_search_missing_key_returns_none(self):
        self.table.insert("P1001", "Paracetamol")
        self.assertIsNone(self.table.search("P9999"))

    def test_duplicate_insert_rejected(self):
        self.table.insert("P1001", "Paracetamol")
        with self.assertRaises(DuplicateKeyError):
            self.table.insert("P1001", "Other")
        self.assertEqual(len(self.table), 1)

    def test_update(self):
        self.table.insert("P1001", "Paracetamol")
        self.table.update("P1001", "Paracetamol 500mg")
        self.assertEqual(self.table.search("P1001"), "Paracetamol 500mg")
        with self.assertRaises(KeyError):
            self.table.update("P9999", "x")

    def test_delete(self):
        self.table.insert("P1001", "Paracetamol")
        self.assertEqual(self.table.delete("P1001"), "Paracetamol")
        self.assertIsNone(self.table.search("P1001"))
        self.assertEqual(len(self.table), 0)
        with self.assertRaises(KeyError):
            self.table.delete("P1001")

    def test_hash_is_deterministic(self):
        # same key -> same home slot, every run (unlike Python's built-in hash())
        a = HashTable(capacity=31)
        b = HashTable(capacity=31)
        self.assertEqual(a.insert("P1042", 1), b.insert("P1042", 1))

    def test_capacity_rounded_to_prime(self):
        self.assertEqual(HashTable(capacity=30).capacity, 31)


class TestLinearProbing(unittest.TestCase):

    def setUp(self):
        # fixed size, every key hashes to slot 0
        self.table = HashTable(capacity=7, max_load_factor=None,
                               hash_function=constant_hash)

    def test_colliding_keys_go_to_consecutive_slots(self):
        self.assertEqual(self.table.insert("A", 1), 0)
        self.assertEqual(self.table.insert("B", 2), 1)
        self.assertEqual(self.table.insert("C", 3), 2)
        self.assertEqual(self.table.collisions, 2)

    def test_probe_count(self):
        for k in "ABC":
            self.table.insert(k, k)
        _, index, probes = self.table.search_with_stats("C")
        self.assertEqual((index, probes), (2, 3))

    def test_wrap_around(self):
        table = HashTable(capacity=5, max_load_factor=None,
                          hash_function=lambda k, c: 4)   # home slot = last slot
        self.assertEqual(table.insert("A", 1), 4)
        self.assertEqual(table.insert("B", 2), 0)          # wraps to the start

    def test_search_continues_past_tombstone(self):
        for k in "ABC":
            self.table.insert(k, k)
        self.table.delete("B")                             # slot 1 -> DELETED
        self.assertEqual(self.table.slot_states()[1], SlotState.DELETED)
        self.assertEqual(self.table.search("C"), "C")      # must probe past slot 1

    def test_insert_reuses_tombstone(self):
        for k in "ABC":
            self.table.insert(k, k)
        self.table.delete("B")
        self.assertEqual(self.table.insert("D", "D"), 1)   # reuses slot 1

    def test_full_table_raises_overflow(self):
        for k in "ABCDEFG":
            self.table.insert(k, k)
        with self.assertRaises(OverflowError):
            self.table.insert("H", "H")
        self.assertEqual(self.table.search("G"), "G")      # full lap search still works
        self.assertIsNone(self.table.search("Z"))          # absent key terminates


class TestResizing(unittest.TestCase):

    def test_table_grows_and_keeps_all_keys(self):
        table = HashTable(capacity=5, max_load_factor=0.7)
        keys = [f"P{1000 + i}" for i in range(50)]
        for i, k in enumerate(keys):
            table.insert(k, i)
        self.assertGreater(table.capacity, 5)
        self.assertLessEqual(table.load_factor, 0.7)
        for i, k in enumerate(keys):
            self.assertEqual(table.search(k), i)
        self.assertEqual(len(table), 50)


if __name__ == "__main__":
    unittest.main()