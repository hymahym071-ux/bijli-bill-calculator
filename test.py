from models import Customer, DomesticCustomer, CommercialCustomer, Bill

customers = [
    DomesticCustomer("1001", "ali khan", 1200, 1450),
    CommercialCustomer("2002", "khan general store", 500, 800),
]

for c in customers:
    print(Bill(c, "October 2026"))

try:
    Customer("9999", "test", 0, 10)
except TypeError as e:
    print("Error:", e)