from models import (DomesticCustomer, CommercialCustomer, Bill,
                    InvalidReadingError, save_customers, load_customers)

MONTH = "October 2026"


def input_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  Sirf number likhein.")


def find_customer(customers, ref_no):
    for c in customers:
        if c.ref_no == ref_no:
            return c
    return None


def add_customer(customers):
    ref_no = input("Reference no: ").strip()
    if find_customer(customers, ref_no):
        print("Ye reference no pehle se mojood hai.")
        return
    name = input("Naam: ")
    kind = input("Type (1 = Domestic, 2 = Commercial): ").strip()
    previous = input_int("Previous reading: ")
    current = input_int("Current reading: ")
    cls = DomesticCustomer if kind == "1" else CommercialCustomer
    try:
        customer = cls(ref_no, name, previous, current)
    except InvalidReadingError as e:
        print("Ghalti:", e)
        return
    customers.append(customer)
    save_customers(customers)
    print("Customer add ho gaya:", customer)


def show_bill(customers):
    c = find_customer(customers, input("Reference no: ").strip())
    if c:
        print(Bill(c, MONTH))
    else:
        print("Customer nahi mila.")


def list_customers(customers):
    if not customers:
        print("Abhi koi customer nahi.")
        return
    print(f"\n{'Ref':<8}{'Naam':<20}{'Type':<12}{'Units':>6}{'Total (Rs)':>12}")
    print("-" * 58)
    for c in customers:
        bill = Bill(c, MONTH)
        print(f"{c.ref_no:<8}{c.name[:18]:<20}{c.CATEGORY:<12}{c.units:>6}{bill.total:>12,.2f}")


def summary(customers):
    if not customers:
        print("Abhi koi customer nahi.")
        return
    bills = [Bill(c, MONTH) for c in customers]
    top = max(customers, key=lambda c: c.units)
    print(f"\nTotal customers : {len(customers)}")
    print(f"Total units     : {sum(c.units for c in customers)}")
    print(f"Total amount    : Rs {sum(b.total for b in bills):,.2f}")
    print(f"Sab se zyada    : {top.name} ({top.units} units)")


def main():
    customers = load_customers()
    menu = {
        "1": ("Naya customer add karein", add_customer),
        "2": ("Saare customers", list_customers),
        "3": ("Bill dekhein", show_bill),
        "4": ("Summary", summary),
    }
    while True:
        print("\n===== BIJLI BILL CALCULATOR =====")
        for key, (label, _) in menu.items():
            print(f"{key}. {label}")
        print("0. Exit")
        choice = input("Option chunein: ").strip()
        if choice == "0":
            print("Allah Hafiz!")
            break
        elif choice in menu:
            menu[choice][1](customers)
        else:
            print("Ghalat option.")


if __name__ == "__main__":
    main()