from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import openpyxl
from io import BytesIO

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# === Models ===
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, default=0)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    product = db.relationship('Product')
    customer = db.relationship('Customer')

# === ROUTES ===

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'quantity': p.quantity} for p in products])

@app.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    p = Product(name=data['name'], quantity=data.get('quantity', 0))
    db.session.add(p)
    db.session.commit()
    return jsonify({'id': p.id, 'name': p.name, 'quantity': p.quantity}), 201

@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([{'id': c.id, 'name': c.name, 'email': c.email} for c in customers])

@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    c = Customer(name=data['name'], email=data.get('email'))
    db.session.add(c)
    db.session.commit()
    return jsonify({'id': c.id, 'name': c.name, 'email': c.email}), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([
        {
            'id': o.id,
            'product': {'id': o.product.id, 'name': o.product.name},
            'customer': {'id': o.customer.id, 'name': o.customer.name},
            'quantity': o.quantity
        } for o in orders
    ])

@app.route('/orders', methods=['POST'])
def add_order():
    data = request.get_json()
    prod = Product.query.get_or_404(data['product_id'])
    cust = Customer.query.get_or_404(data['customer_id'])
    if prod.quantity < data['quantity']:
        return jsonify({'error': 'Insufficient stock'}), 400
    o = Order(product_id=prod.id, customer_id=cust.id, quantity=data['quantity'])
    prod.quantity -= data['quantity']
    db.session.add(o)
    db.session.commit()
    return jsonify({'id': o.id, 'product_id': prod.id, 'customer_id': cust.id, 'quantity': o.quantity}), 201

# === PRODUCTS UI ===
@app.route('/view_products')
def view_products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/add_product_form', methods=['POST'])
def add_product_form():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    p = Product(name=name, quantity=quantity)
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('view_products'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('view_products'))

# === CUSTOMERS UI ===
@app.route('/view_customers')
def view_customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/add_customer_form', methods=['POST'])
def add_customer_form():
    name = request.form['name']
    email = request.form['email']
    c = Customer(name=name, email=email)
    db.session.add(c)
    db.session.commit()
    return redirect(url_for('view_customers'))

@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('view_customers'))

# === ORDERS UI ===
@app.route('/view_orders')
def view_orders():
    orders = Order.query.all()
    customers = Customer.query.all()
    products = Product.query.all()
    return render_template('orders.html', orders=orders, customers=customers, products=products)

@app.route('/add_order_form', methods=['POST'])
def add_order_form():
    customer_id = int(request.form['customer_id'])
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])

    product = Product.query.get(product_id)
    if product.quantity < quantity:
        return "Δεν υπάρχει αρκετό απόθεμα!", 400

    order = Order(product_id=product_id, customer_id=customer_id, quantity=quantity)
    product.quantity -= quantity
    db.session.add(order)
    db.session.commit()
    return redirect(url_for('view_orders'))

# === REPORTS ===
@app.route('/product_report')
def product_report():
    products = Product.query.all()
    orders = Order.query.all()
    sales = {}
    for order in orders:
        if order.product_id not in sales:
            sales[order.product_id] = 0
        sales[order.product_id] += order.quantity

    sales_report = []
    for product in products:
        quantity_sold = sales.get(product.id, 0)
        sales_report.append({'name': product.name, 'sold': quantity_sold})
    sales_report.sort(key=lambda x: x['sold'], reverse=True)
    return render_template('product_report.html', report=sales_report)

@app.route('/export_product_report')
def export_product_report():
    products = Product.query.all()
    orders = Order.query.all()

    sales = {}
    for order in orders:
        if order.product_id not in sales:
            sales[order.product_id] = 0
        sales[order.product_id] += order.quantity

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Πωλήσεις Προϊόντων"
    ws.append(["Προϊόν", "Πωληθέντα Τεμάχια"])

    for product in products:
        sold = sales.get(product.id, 0)
        ws.append([product.name, sold])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output, as_attachment=True, download_name="product_report.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@app.route('/customer_report')
def customer_report():
    customers = Customer.query.all()
    orders = Order.query.all()
    customer_sales = {}
    for order in orders:
        if order.customer_id not in customer_sales:
            customer_sales[order.customer_id] = 0
        customer_sales[order.customer_id] += order.quantity

    customer_report = []
    for customer in customers:
        total_bought = customer_sales.get(customer.id, 0)
        customer_report.append({'name': customer.name, 'total_bought': total_bought})
    customer_report.sort(key=lambda x: x['total_bought'], reverse=True)
    return render_template('customer_report.html', report=customer_report)

@app.route('/low_stock')
def low_stock():
    products = Product.query.all()
    if not products:
        return render_template('low_stock.html', products=[], no_products=True)

    low_stock_products = Product.query.filter(Product.quantity < 10).all()
    return render_template('low_stock.html', products=low_stock_products, no_products=False)

# === DB INIT ===
with app.app_context():
    db.create_all()

# === RUN APP CORRECTLY ON RENDER ===
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
