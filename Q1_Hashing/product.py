"""
Entity classes for the pharmacy inventory.

Product           - abstract base class: attributes every product has
Medicine          - a medicine (adds dosage, prescription flag)
HealthSupplement  - a supplement / vitamin (adds category, servings)

These classes only describe products. They do not know about the hash table,
so the hash table stays generic and these classes stay simple.
"""

from abc import ABC, abstractmethod
from datetime import date


class Product(ABC):
    """Common data for every pharmacy product.

    Attributes (all validated by property setters):
        product_id     : str   - unique key used by the hash table, e.g. "P1042"
        name           : str   - product name, e.g. "Paracetamol 500mg"
        price          : float - selling price in RM, must be >= 0
        stock_quantity : int   - units in stock, must be >= 0
        manufacturer   : str   - company that makes the product
        expiry_date    : date  - expiry date of the current stock
    """

    def __init__(self, product_id, name, price, stock_quantity,
                 manufacturer, expiry_date):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock_quantity = stock_quantity
        self.manufacturer = manufacturer
        self.expiry_date = expiry_date

    # ---------------- validated attributes ---------------- #
    @property
    def product_id(self):
        return self._product_id

    @product_id.setter
    def product_id(self, value):
        value = str(value).strip().upper()          # "p1042 " -> "P1042"
        if not value:
            raise ValueError("Product ID cannot be empty")
        self._product_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Product name cannot be empty")
        self._name = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        value = float(value)
        if value < 0:
            raise ValueError("Price cannot be negative")
        self._price = round(value, 2)               # money: 2 decimal places

    @property
    def stock_quantity(self):
        return self._stock_quantity

    @stock_quantity.setter
    def stock_quantity(self, value):
        value = int(value)
        if value < 0:
            raise ValueError("Stock quantity cannot be negative")
        self._stock_quantity = value

    @property
    def manufacturer(self):
        return self._manufacturer

    @manufacturer.setter
    def manufacturer(self, value):
        self._manufacturer = str(value).strip() or "Unknown"

    @property
    def expiry_date(self):
        return self._expiry_date

    @expiry_date.setter
    def expiry_date(self, value):
        if isinstance(value, str):                  # accept "YYYY-MM-DD" text
            value = date.fromisoformat(value.strip())
        if not isinstance(value, date):
            raise ValueError("Expiry date must be a date (YYYY-MM-DD)")
        self._expiry_date = value

    # ---------------- behaviour ---------------- #
    def is_expired(self, today=None):
        """True if the expiry date has passed."""
        return self.expiry_date < (today or date.today())

    @abstractmethod
    def product_type(self):
        """Name of the product type - each subclass must define it."""

    def extra_details(self):
        """Type-specific fields as (label, value) pairs. Subclasses extend this."""
        return []

    def summary(self):
        """One-line description, used in search results and listings."""
        return (f"ID: {self.product_id} | Name: {self.name} | "
                f"Price: RM{self.price:.2f} | Stock: {self.stock_quantity}")

    def details(self):
        """Multi-line full description of the product."""
        lines = [
            f"Product ID     : {self.product_id}",
            f"Type           : {self.product_type()}",
            f"Name           : {self.name}",
            f"Price          : RM{self.price:.2f}",
            f"Stock Quantity : {self.stock_quantity}",
            f"Manufacturer   : {self.manufacturer}",
            f"Expiry Date    : {self.expiry_date.isoformat()}"
            + ("  (EXPIRED)" if self.is_expired() else ""),
        ]
        lines += [f"{label:<15}: {value}" for label, value in self.extra_details()]
        return "\n".join(lines)

    def __str__(self):
        return self.summary()

    def __repr__(self):
        return f"{type(self).__name__}({self.product_id!r}, {self.name!r})"


class Medicine(Product):
    """A medicine.

    Extra attributes:
        dosage                : str  - strength and form, e.g. "500mg tablet"
        requires_prescription : bool - True if a doctor's prescription is needed
    """

    def __init__(self, product_id, name, price, stock_quantity,
                 manufacturer, expiry_date, dosage, requires_prescription=False):
        super().__init__(product_id, name, price, stock_quantity,
                         manufacturer, expiry_date)
        self.dosage = str(dosage).strip()
        self.requires_prescription = bool(requires_prescription)

    def product_type(self):
        return "Medicine"

    def extra_details(self):
        return [("Dosage", self.dosage),
                ("Prescription", "Required" if self.requires_prescription else "Not required")]


class HealthSupplement(Product):
    """A health supplement, e.g. vitamins or fish oil.

    Extra attributes:
        category               : str - e.g. "Vitamin", "Mineral", "Herbal"
        servings_per_container : int - number of servings in one pack
    """

    def __init__(self, product_id, name, price, stock_quantity,
                 manufacturer, expiry_date, category, servings_per_container):
        super().__init__(product_id, name, price, stock_quantity,
                         manufacturer, expiry_date)
        self.category = str(category).strip()
        self.servings_per_container = servings_per_container

    @property
    def servings_per_container(self):
        return self._servings_per_container

    @servings_per_container.setter
    def servings_per_container(self, value):
        value = int(value)
        if value <= 0:
            raise ValueError("Servings per container must be positive")
        self._servings_per_container = value

    def product_type(self):
        return "Health Supplement"

    def extra_details(self):
        return [("Category", self.category),
                ("Servings/Pack", self.servings_per_container)]


