"""
Bijli Bill Calculator - models.py
Saari classes yahan hain: Customer, DomesticCustomer, CommercialCustomer, Bill
Note: rates sirf practice ke liye hain, asal company rates nahi.
"""
from abc import ABC, abstractmethod
import json
import os


class InvalidReadingError(Exception):
    """Jab meter reading ghalat ho to ye error uthta hai."""


class Customer(ABC):
    """Har customer ka base (parent) class."""

    GST_RATE = 0.17
    TV_FEE = 35
    CATEGORY = "General"

    def __init__(self, ref_no, name, previous, current):
        self.ref_no = ref_no
        self.name = name.strip().title()
        self.set_readings(previous, current)

    def set_readings(self, previous, current):
        if previous < 0 or current < 0:
            raise InvalidReadingError("Reading negative nahi ho sakti.")
        if current < previous:
            raise InvalidReadingError("Current reading previous se kam nahi ho sakti.")
        self.__previous = previous
        self.__current = current

    @property
    def previous(self):
        return self.__previous

    @property
    def current(self):
        return self.__current

    @property
    def units(self):
        return self.__current - self.__previous

    @abstractmethod
    def energy_charges(self):
        """Har child class apna tareeqa khud likhegi."""

    def fixed_charges(self):
        return 0

    def to_dict(self):
        return {
            "type": self.CATEGORY,
            "ref_no": self.ref_no,
            "name": self.name,
            "previous": self.previous,
            "current": self.current,
        }

    def __str__(self):
        return f"{self.name} ({self.CATEGORY}) - {self.units} units"


class DomesticCustomer(Customer):
    """Ghar ka meter: slab system."""

    CATEGORY = "Domestic"
    SLABS = [(100, 10), (100, 15), (100, 20), (None, 30)]

    def energy_charges(self):
        remaining = self.units
        total = 0
        for size, rate in self.SLABS:
            if size is None or remaining <= size:
                total += remaining * rate
                break
            total += size * rate
            remaining -= size
        return total


class CommercialCustomer(Customer):
    """Dukaan / office ka meter: flat rate + fixed charges."""

    CATEGORY = "Commercial"
    RATE = 40
    FIXED = 500

    def energy_charges(self):
        return self.units * self.RATE

    def fixed_charges(self):
        return self.FIXED


class Bill:
    """Aik customer ka aik mahine ka bill (Bill ke andar Customer = composition)."""

    LATE_SURCHARGE = 0.10

    def __init__(self, customer, month):
        self.customer = customer
        self.month = month
        self.energy = customer.energy_charges()
        self.fixed = customer.fixed_charges()
        self.gst = round(self.energy * Customer.GST_RATE, 2)
        self.tv_fee = Customer.TV_FEE
        self.total = round(self.energy + self.fixed + self.gst + self.tv_fee, 2)
        self.late_total = round(self.total * (1 + self.LATE_SURCHARGE), 2)

    def __str__(self):
        c = self.customer
        line = "-" * 38
        return "\n".join([
            "=" * 38,
            f"  BIJLI BILL - {self.month}",
            line,
            f"  Ref No   : {c.ref_no}",
            f"  Naam     : {c.name}",
            f"  Category : {c.CATEGORY}",
            f"  Reading  : {c.previous} -> {c.current}",
            f"  Units    : {c.units}",
            line,
            f"  Energy charges : Rs {self.energy:>10,.2f}",
            f"  Fixed charges  : Rs {self.fixed:>10,.2f}",
            f"  GST (17%)      : Rs {self.gst:>10,.2f}",
            f"  TV fee         : Rs {self.tv_fee:>10,.2f}",
            line,
            f"  TOTAL          : Rs {self.total:>10,.2f}",
            f"  Late payment   : Rs {self.late_total:>10,.2f}",
            "=" * 38,
        ])


# ---------- Save / Load (JSON) ----------

CUSTOMER_TYPES = {"Domestic": DomesticCustomer, "Commercial": CommercialCustomer}


def create_customer(data):
    """Dict se sahi class ka object banata hai."""
    cls = CUSTOMER_TYPES[data["type"]]
    return cls(data["ref_no"], data["name"], data["previous"], data["current"])


def save_customers(customers, filename="customers.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump([c.to_dict() for c in customers], f, indent=2)


def load_customers(filename="customers.json"):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [create_customer(d) for d in json.load(f)]