"""
inventory_system.py
-------------------
Command-line Pharmacy Inventory System (Question 1, Task 3).

Two layers:
  InventoryService - the logic (insert/search/edit/delete). No input()/print(),
                     so it can be reused by another interface or by tests.
  InventoryCLI     - the menu: reads user input and prints results.

Run this file to start the program:  python inventory_system.py
"""

import time

from hash_table import HashTable, DuplicateKeyError
from product import Medicine, HealthSupplement
from array_search import linear_search
from sample_data import create_sample_products, load_products


# ====================================================================== #
# Logic layer
# ====================================================================== #
class InventoryService:
    """Stores products in a hash table, and the same products in a 1-D array
    so that every search can be compared between the two structures."""

    def __init__(self, capacity=HashTable.DEFAULT_CAPACITY):
        self.table = HashTable(capacity)
        self.array = []

    def load(self, products):
        return load_products(self.table, self.array, products)

    def insert(self, product):
        """Insert into both structures. Returns (slot, resized)."""
        old_capacity = self.table.capacity
        slot = self.table.insert(product.product_id, product)  # raises DuplicateKeyError
        self.array.append(product)
        return slot, self.table.capacity != old_capacity

    def search(self, product_id):
        """Search both structures and time each search in nanoseconds.

        Returns a dict with the product and the statistics of each search.
        """
        start = time.perf_counter_ns()
        product, slot, probes = self.table.search_with_stats(product_id)
        hash_ns = time.perf_counter_ns() - start

        start = time.perf_counter_ns()
        _, index, comparisons = linear_search(self.array, product_id)
        array_ns = time.perf_counter_ns() - start

        return {"product": product, "slot": slot, "probes": probes, "hash_ns": hash_ns,
                "index": index, "comparisons": comparisons, "array_ns": array_ns}

    def contains(self, product_id):
        return product_id in self.table

    def delete(self, product_id):
        """Remove from both structures. Raises KeyError if absent."""
        product = self.table.delete(product_id)
        self.array.remove(product)
        return product

    def all_products(self):
        """(slot, product) for every product, in slot order."""
        return [(slot, product) for slot, _, product in self.table.items()]

    def status(self):
        return {"capacity": self.table.capacity, "size": len(self.table),
                "load_factor": self.table.load_factor,
                "collisions": self.table.collisions,
                "states": self.table.slot_states()}


# ====================================================================== #
# Input helpers - keep asking until the user types a valid value
# ====================================================================== #
def ask(prompt, convert=str, default=None):
    """Ask for a value and convert it. Empty input returns default (if given).

    convert can be any function that raises ValueError on bad input.
    """
    while True:
        text = input(prompt).strip()
        if text == "" and default is not None:
            return default
        try:
            value = convert(text)
            if isinstance(value, str) and value == "":
                raise ValueError("value cannot be empty")
            return value
        except ValueError as error:
            print(f"  Invalid input ({error}). Please try again.")


def non_negative(convert):
    def check(text):
        value = convert(text)
        if value < 0:
            raise ValueError("must not be negative")
        return value
    return check


def yes_no(text):
    text = text.lower()
    if text in ("y", "yes"):
        return True
    if text in ("n", "no"):
        return False
    raise ValueError("enter y or n")


def iso_date(text):
    from datetime import date
    return date.fromisoformat(text)    # raises ValueError if not YYYY-MM-DD


# ====================================================================== #
# Menu layer
# ====================================================================== #
class InventoryCLI:

    MENU = ("1. Insert Product", "2. Search Product", "3. Edit Product",
            "4. Delete Product", "5. Display All Products",
            "6. View Hash Table Status", "7. Exit")

    def __init__(self, service):
        self.service = service
        self.actions = {"1": self.insert_product, "2": self.search_product,
                        "3": self.edit_product, "4": self.delete_product,
                        "5": self.display_all, "6": self.show_status}

    def run(self):
        print("==== Pharmacy Inventory System ====")
        while True:
            print()
            print("\n".join(self.MENU))
            choice = input("Enter choice: ").strip()
            if choice == "7":
                print("Exiting Inventory System. Goodbye!")
                break
            action = self.actions.get(choice)
            if action is None:
                print("Invalid choice. Please enter a number from 1 to 7.")
            else:
                action()

    # ---------------- 1. Insert ---------------- #
    def insert_product(self):
        kind = ask("Product type (1 = Medicine, 2 = Health Supplement): ",
                   self._product_kind)
        product_id = ask("Enter Product ID: ", lambda t: t.upper())
        if self.service.contains(product_id):      # check early, before asking more
            print(f"Product ID {product_id} already exists. Use Edit instead.")
            return

        common = dict(
            product_id=product_id,
            name=ask("Enter Product Name: "),
            price=ask("Enter Price (RM): ", non_negative(float)),
            stock_quantity=ask("Enter Stock Quantity: ", non_negative(int)),
            manufacturer=ask("Enter Manufacturer: "),
            expiry_date=ask("Enter Expiry Date (YYYY-MM-DD): ", iso_date),
        )
        if kind == "medicine":
            product = Medicine(**common,
                               dosage=ask("Enter Dosage (e.g. 500mg tablet): "),
                               requires_prescription=ask("Requires prescription? (y/n): ", yes_no))
        else:
            product = HealthSupplement(**common,
                                       category=ask("Enter Category (e.g. Vitamin): "),
                                       servings_per_container=ask("Enter Servings per Container: ",
                                                                  self._positive_int))
        try:
            slot, resized = self.service.insert(product)
        except DuplicateKeyError:
            print(f"Product ID {product_id} already exists.")
            return
        if resized:
            print(f"Load factor limit reached: table resized to "
                  f"{self.service.table.capacity} slots and all records rehashed.")
        print(f"Product inserted successfully into slot [{slot}]")

    # ---------------- 2. Search ---------------- #
    def search_product(self):
        product_id = ask("Enter Product ID to search: ", lambda t: t.upper())
        result = self.service.search(product_id)
        if result["product"] is None:
            print(f"Product {product_id} not found.")
        else:
            print("Product Found!")
            print(result["product"].summary())
            print(f"Located at slot [{result['slot']}] after {result['probes']} probe(s)")
        print(f"Search completed in {result['hash_ns'] / 1e9:.9f} seconds "
              f"({result['hash_ns']:,} ns) (Hash Table, {result['probes']} probe(s))")
        print(f"Search completed in {result['array_ns'] / 1e9:.9f} seconds "
              f"({result['array_ns']:,} ns) (Array - same record, "
              f"{result['comparisons']} comparison(s))")
        print("Note: a single search takes only microseconds, so these times vary "
              "between runs; see experiment.py for averaged results.")

    # ---------------- 3. Edit (optional feature) ---------------- #
    def edit_product(self):
        product_id = ask("Enter Product ID to edit: ", lambda t: t.upper())
        product = self.service.search(product_id)["product"]
        if product is None:
            print(f"Product {product_id} not found.")
            return
        print(product.details())
        print("Press Enter to keep the current value. (Product ID cannot be changed.)")

        product.name = ask(f"Name [{product.name}]: ", default=product.name)
        product.price = ask(f"Price [{product.price:.2f}]: ", non_negative(float), product.price)
        product.stock_quantity = ask(f"Stock [{product.stock_quantity}]: ",
                                     non_negative(int), product.stock_quantity)
        product.manufacturer = ask(f"Manufacturer [{product.manufacturer}]: ",
                                   default=product.manufacturer)
        product.expiry_date = ask(f"Expiry Date [{product.expiry_date}]: ",
                                  iso_date, product.expiry_date)
        if isinstance(product, Medicine):
            product.dosage = ask(f"Dosage [{product.dosage}]: ", default=product.dosage)
            current = "y" if product.requires_prescription else "n"
            product.requires_prescription = ask(f"Requires prescription? (y/n) [{current}]: ",
                                                yes_no, product.requires_prescription)
        else:
            product.category = ask(f"Category [{product.category}]: ", default=product.category)
            product.servings_per_container = ask(
                f"Servings per Container [{product.servings_per_container}]: ",
                self._positive_int, product.servings_per_container)
        # The object is shared by the hash table and the array, so both see the change.
        print("Product updated successfully.")
        print(product.details())

    # ---------------- 4. Delete (optional feature) ---------------- #
    def delete_product(self):
        product_id = ask("Enter Product ID to delete: ", lambda t: t.upper())
        result = self.service.search(product_id)
        if result["product"] is None:
            print(f"Product {product_id} not found.")
            return
        print(result["product"].summary())
        if ask("Are you sure you want to delete this product? (y/n): ", yes_no):
            self.service.delete(product_id)
            print(f"Product {product_id} deleted. Slot [{result['slot']}] is now marked DELETED.")
        else:
            print("Delete cancelled.")

    # ---------------- 5. Display all (optional feature) ---------------- #
    def display_all(self):
        rows = self.service.all_products()
        if not rows:
            print("The inventory is empty.")
            return
        header = (f"{'Slot':<6}{'Home':<6}{'ID':<8}{'Type':<19}{'Name':<24}"
                  f"{'Price (RM)':>11}{'Stock':>7}")
        print(header)
        print("-" * len(header))
        for slot, p in rows:
            home = self.service.table.home_slot(p.product_id)
            print(f"{slot:<6}{home:<6}{p.product_id:<8}{p.product_type():<19}"
                  f"{p.name[:23]:<24}{p.price:>11.2f}{p.stock_quantity:>7}")
        print(f"Total products: {len(rows)}  (Slot != Home means the record was "
              f"moved by linear probing)")

    # ---------------- 6. Status (optional feature) ---------------- #
    def show_status(self):
        s = self.service.status()
        print(f"Capacity (slots)   : {s['capacity']}")
        print(f"Products stored    : {s['size']}")
        print(f"Load factor        : {s['load_factor']:.2f}")
        print(f"Collisions         : {s['collisions']}")
        symbols = {"EMPTY": ".", "OCCUPIED": "#", "DELETED": "x"}
        print("Slot map (# occupied, . empty, x deleted):")
        line = "".join(symbols[state.name] for state in s["states"])
        for start in range(0, len(line), 50):
            print(f"  [{start:>4}] {line[start:start + 50]}")

    # ---------------- converters used by the prompts ---------------- #
    @staticmethod
    def _product_kind(text):
        if text == "1":
            return "medicine"
        if text == "2":
            return "supplement"
        raise ValueError("enter 1 or 2")

    @staticmethod
    def _positive_int(text):
        value = int(text)
        if value <= 0:
            raise ValueError("must be greater than 0")
        return value


def main():
    service = InventoryService()
    placements = service.load(create_sample_products())
    print(f"Loaded {len(placements)} pre-defined products into a hash table "
          f"of {service.table.capacity} slots.")
    try:
        InventoryCLI(service).run()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting Inventory System. Goodbye!")


if __name__ == "__main__":
    main()