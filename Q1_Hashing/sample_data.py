"""
sample_data.py
--------------
Pre-defined pharmacy records that are loaded when the system starts
(Question 1, Task 2: "insert a few pre-defined records into the hash table").
"""

from product import Medicine, HealthSupplement


def create_sample_products():
    """Return a list of pre-defined products (new objects every call)."""
    return [
        # Medicine(id, name, price, stock, manufacturer, expiry, dosage, prescription?)
        Medicine("P1001", "Paracetamol 500mg", 5.90, 120, "Panadol Co.", "2027-12-31", "500mg tablet", False),
        Medicine("P1002", "Ibuprofen 200mg", 8.50, 80, "Nurofen Ltd.", "2027-08-15", "200mg tablet", False),
        Medicine("P1003", "Amoxicillin 250mg", 15.00, 40, "GSK", "2027-03-01", "250mg capsule", True),
        Medicine("P1004", "Cetirizine 10mg", 12.30, 65, "Zyrtec Inc.", "2028-01-20", "10mg tablet", False),
        Medicine("P1005", "Omeprazole 20mg", 18.90, 30, "AstraZeneca", "2027-11-11", "20mg capsule", True),
        Medicine("P1006", "Loratadine 10mg", 10.50, 55, "Clarityne", "2028-05-05", "10mg tablet", False),
        Medicine("P1007", "Metformin 500mg", 9.80, 70, "Merck", "2027-09-30", "500mg tablet", True),
        HealthSupplement("S2001", "Vitamin C 1000mg", 32.50, 40, "Blackmores", "2028-06-30", "Vitamin", 60),
        HealthSupplement("S2002", "Fish Oil Omega-3", 45.00, 25, "Nature's Way", "2028-02-28", "Fatty Acid", 90),
        HealthSupplement("S2003", "Calcium + Vitamin D3", 28.90, 35, "Caltrate", "2027-10-10", "Mineral", 60),
    ]


def load_products(table, array, products):
    """Insert every product into both the hash table and the 1-D array.

    Returns a list of (product, slot_index) so the caller can show where
    each record was placed.
    """
    placements = []
    for product in products:
        slot = table.insert(product.product_id, product)   # key = ID, value = object
        array.append(product)                               # same data, same order
        placements.append((product, slot))
    return placements


