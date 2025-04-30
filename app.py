### 🔹 Βήμα 1: Customers

**app.py**:
```python
@app.route("/customers")
def get_customers():
    customers = Customer.query.all()
    return render_template("customers.html", customers=customers)
```

**templates/customers.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Πελάτες</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-5">
    <h1 class="mb-4">Λίστα Πελατών</h1>
    <ul class="list-group mb-5">
        {% for customer in customers %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {{ customer.name }}
                <form action="/delete_customer/{{ customer.id }}" method="POST" style="display:inline;">
                    <button type="submit" class="btn btn-sm btn-danger">Διαγραφή</button>
                </form>
            </li>
        {% endfor %}
    </ul>

    <h2 class="mb-3">Προσθήκη Νέου Πελάτη</h2>
    <form action="/add_customer_form" method="POST">
        <div class="mb-3">
            <label class="form-label">Όνομα</label>
            <input type="text" name="name" class="form-control" required>
        </div>
        <button type="submit" class="btn btn-success">Προσθήκη</button>
    </form>
</body>
</html>
```

---

### 🔹 Βήμα 2: Orders

**app.py**:
```python
@app.route("/orders")
def get_orders():
    orders = Order.query.all()
    return render_template("orders.html", orders=orders)
```

**templates/orders.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Παραγγελίες</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-5">
    <h1 class="mb-4">Λίστα Παραγγελιών</h1>
    <ul class="list-group mb-5">
        {% for order in orders %}
            <li class="list-group-item">
                Πελάτης: {{ order.customer.name }} - Προϊόν: {{ order.product.name }} - Ποσότητα: {{ order.quantity }}
            </li>
        {% endfor %}
    </ul>

    <h2 class="mb-3">Προσθήκη Παραγγελίας</h2>
    <form action="/add_order_form" method="POST">
        <div class="mb-3">
            <label class="form-label">ID Πελάτη</label>
            <input type="number" name="customer_id" class="form-control" required>
        </div>
        <div class="mb-3">
            <label class="form-label">ID Προϊόντος</label>
            <input type="number" name="product_id" class="form-control" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Ποσότητα</label>
            <input type="number" name="quantity" class="form-control" required>
        </div>
        <button type="submit" class="btn btn-success">Προσθήκη</button>
    </form>
</body>
</html>
```

---

### 🔹 Βήμα 3: Product Report

**app.py**:
```python
@app.route("/product_report")
def product_report():
    return render_template("product_report.html")
```

**templates/product_report.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Αναφορά Πωλήσεων Προϊόντων</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-5">
    <h1 class="mb-4">Αναφορά Πωλήσεων Προϊόντων</h1>
    <form action="/product_report" method="POST">
        <div class="mb-3">
            <label class="form-label">Ημερομηνία Έναρξης</label>
            <input type="date" name="start_date" class="form-control">
        </div>
        <div class="mb-3">
            <label class="form-label">Ημερομηνία Λήξης</label>
            <input type="date" name="end_date" class="form-control">
        </div>
        <button type="submit" class="btn btn-primary">Εμφάνιση Αναφοράς</button>
    </form>
</body>
</html>
```

---

### 🔹 Βήμα 4: Customer Report

**app.py**:
```python
@app.route("/customer_report")
def customer_report():
    return render_template("customer_report.html")
```

**templates/customer_report.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Αναφορά Πωλήσεων Πελατών</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-5">
    <h1 class="mb-4">Αναφορά Πωλήσεων Πελατών</h1>
    <form action="/customer_report" method="POST">
        <div class="mb-3">
            <label class="form-label">Ημερομηνία Έναρξης</label>
            <input type="date" name="start_date" class="form-control">
        </div>
        <div class="mb-3">
            <label class="form-label">Ημερομηνία Λήξης</label>
            <input type="date" name="end_date" class="form-control">
        </div>
        <button type="submit" class="btn btn-primary">Εμφάνιση Αναφοράς</button>
    </form>
</body>
</html>
```

---

### 🔹 Βήμα 5: Low Stock

**app.py**:
```python
@app.route("/low_stock")
def low_stock():
    threshold = 10
    low_stock_items = Product.query.filter(Product.quantity <= threshold).all()
    return render_template("low_stock.html", products=low_stock_items)
```

**templates/low_stock.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Χαμηλό Απόθεμα</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="container mt-5">
    <h1 class="mb-4">Προϊόντα με Χαμηλό Απόθεμα</h1>
    <ul class="list-group">
        {% for product in products %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {{ product.name }}
                <span class="badge bg-danger rounded-pill">{{ product.quantity }} τεμάχια</span>
            </li>
        {% endfor %}
    </ul>
</body>
</html>
```

---

Αφού τα προσθέσεις:
1. **Άνοιξε CMD στο φάκελο `inventory_app`**.
2. Εκτέλεσε:
```bash
git add .
git commit -m "Add templates and routes for all pages"
git push
```
3. Μετά μπες στο Render και κάνε **Manual Deploy** αν δεν ξεκινήσει μόνο του.

Πες μου όταν τελειώσεις για να ελέγξουμε τη λειτουργία ή να φτιάξουμε login. 🚀
