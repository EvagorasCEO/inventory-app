from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from openpyxl import Workbook
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SECRET_KEY'] = 'secret_key'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product', backref='orders')
    customer = db.relationship('Customer', backref='orders')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/products', methods=['GET'])
@login_required
def view_products():
    products = Product.query.all()
    return render_template('pages/products.html', products=products)

@app.route('/add_product_form', methods=['POST'])
@login_required
def add_product():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    db.session.add(Product(name=name, quantity=quantity))
    db.session.commit()
    return redirect(url_for('view_products'))

@app.route('/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('view_products'))

@app.route('/customers')
@login_required
def view_customers():
    customers = Customer.query.all()
    return render_template('pages/customers.html', customers=customers)

@app.route('/add_customer_form', methods=['POST'])
@login_required
def add_customer():
    name = request.form['name']
    email = request.form['email']
    db.session.add(Customer(name=name, email=email))
    db.session.commit()
    return redirect(url_for('view_customers'))

@app.route('/delete_customer/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('view_customers'))

@app.route('/orders')
@login_required
def view_orders():
    orders = Order.query.all()
    return render_template('pages/orders.html', orders=orders)

@app.route('/add_order_form', methods=['POST'])
@login_required
def add_order():
    product_id = int(request.form['product_id'])
    customer_id = int(request.form['customer_id'])
    quantity = int(request.form['quantity'])
    db.session.add(Order(product_id=product_id, customer_id=customer_id, quantity=quantity))
    db.session.commit()
    return redirect(url_for('view_orders'))

@app.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get(order_id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('view_orders'))

@app.route('/product_report')
@login_required
def product_report():
    products = Product.query.all()
    no_products = len(products) == 0
    low_stock = [p for p in products if p.quantity <= 10]
    return render_template('reports/product_report.html', products=low_stock, no_products=no_products)

@app.route('/customer_report')
@login_required
def customer_report():
    orders = Order.query.all()
    return render_template('reports/customer_report.html', orders=orders)

@app.route('/export_products')
@login_required
def export_products():
    products = Product.query.all()
    wb = Workbook()
    ws = wb.active
    ws.append(['ID', 'Όνομα', 'Ποσότητα'])
    for p in products:
        ws.append([p.id, p.name, p.quantity])
    filename = 'products_export.xlsx'
    wb.save(filename)
    return f'Αρχείο εξήχθη: {filename}'

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
