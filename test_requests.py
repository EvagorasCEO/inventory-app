import requests

BASE_URL = "http://127.0.0.1:5000"

# 1. Προσθήκη προϊόντος
def add_product(name, quantity):
    response = requests.post(f"{BASE_URL}/products", json={
        "name": name,
        "quantity": quantity
    })
    print("📦 Προϊόν:", response.json())

# 2. Προσθήκη πελάτη
def add_customer(name, email):
    response = requests.post(f"{BASE_URL}/customers", json={
        "name": name,
        "email": email
    })
    print("👤 Πελάτης:", response.json())

# 3. Δημιουργία παραγγελίας
def add_order(product_id, customer_id, quantity):
    response = requests.post(f"{BASE_URL}/orders", json={
        "product_id": product_id,
        "customer_id": customer_id,
        "quantity": quantity
    })
    print("🧾 Παραγγελία:", response.json())

# === ΔΟΚΙΜΕΣ ===

# Βήμα 1: Πρόσθεσε προϊόντα
add_product("Nescafe Gold 200g", 50)
add_product("Lipton Tea 100x", 120)

# Βήμα 2: Πρόσθεσε πελάτες
add_customer("Kafekopteio Ltd", "info@kafe.com")
add_customer("To Kentriko", "kentriko@cyprus.com")

# Βήμα 3: Κάνε μια παραγγελία (π.χ. πελάτης 1, προϊόν 1, ποσότητα 10)
add_order(product_id=1, customer_id=1, quantity=10)
