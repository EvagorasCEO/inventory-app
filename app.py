from flask import Flask, request, jsonify, render_template, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import os
import openpyxl
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Μπορείς να το αλλάξεις με ένα ισχυρό κλειδί
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

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

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === Routes ===
@app.route('/')
def home():
    return render_template('home.html')

@app.route("/products")
def get_products():
    products = Product.query.all()
    return render_template("products.html", products=products)


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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Λάθος στοιχεία!')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
