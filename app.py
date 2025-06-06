from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ==== Μοντέλα ====

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    license_number = db.Column(db.String(50))
    notes = db.Column(db.Text)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), nullable=False)
    model = db.Column(db.String(100))
    year = db.Column(db.String(10))
    owner = db.Column(db.String(100))
    license_expiry = db.Column(db.String(20))
    insurance_expiry = db.Column(db.String(20))
    mot_expiry = db.Column(db.String(20))
    notes = db.Column(db.Text)

# ==== Login ====

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            return redirect(url_for('index'))
        else:
            error = "Λάθος όνομα χρήστη ή κωδικός."
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ==== Αρχική Σελίδα ====

@app.route('/')
@login_required
def index():
    return render_template('dashboard.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return redirect(url_for('index'))

# ==== Προϊόντα ====

@app.route('/view_products')
@login_required
def view_products():
    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/add_product_form', methods=['POST'])
@login_required
def add_product_form():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    new_product = Product(name=name, quantity=quantity)
    db.session.add(new_product)
    db.session.commit()
    return redirect(url_for('view_products'))

@app.route('/delete_product/<int:id>', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('view_products'))

# ==== Πελάτες ====

@app.route('/view_customers')
@login_required
def view_customers():
    customers = Customer.query.all()
    return render_template('customers.html', customers=customers)

@app.route('/add_customer_form', methods=['POST'])
@login_required
def add_customer_form():
    name = request.form['name']
    customer = Customer(name=name)
    db.session.add(customer)
    db.session.commit()
    return redirect(url_for('view_customers'))

@app.route('/delete_customer/<int:id>', methods=['POST'])
@login_required
def delete_customer(id):
    customer = Customer.query.get(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect(url_for('view_customers'))

# ==== Παραγγελίες ====

@app.route('/view_orders')
@login_required
def view_orders():
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)

@app.route('/add_order_form', methods=['POST'])
@login_required
def add_order_form():
    customer_name = request.form['customer_name']
    product_name = request.form['product_name']
    quantity = int(request.form['quantity'])
    new_order = Order(customer_name=customer_name, product_name=product_name, quantity=quantity)
    db.session.add(new_order)
    db.session.commit()
    return redirect(url_for('view_orders'))

@app.route('/delete_order/<int:id>', methods=['POST'])
@login_required
def delete_order(id):
    order = Order.query.get(id)
    db.session.delete(order)
    db.session.commit()
    return redirect(url_for('view_orders'))

# ==== Reports ====

@app.route('/product_report')
@login_required
def product_report():
    products = Product.query.all()
    return render_template('product_report.html', products=products)

@app.route('/customer_report')
@login_required
def customer_report():
    customers = Customer.query.all()
    return render_template('customer_report.html', customers=customers)

# ==== Drivers ====

@app.route('/drivers')
@login_required
def view_drivers():
    drivers = Driver.query.all()
    return render_template('drivers.html', drivers=drivers)

@app.route('/add_driver', methods=['POST'])
@login_required
def add_driver():
    full_name = request.form['full_name']
    phone = request.form.get('phone')
    license_number = request.form.get('license_number')
    notes = request.form.get('notes')

    new_driver = Driver(
        full_name=full_name,
        phone=phone,
        license_number=license_number,
        notes=notes
    )
    db.session.add(new_driver)
    db.session.commit()
    return redirect(url_for('view_drivers'))

@app.route('/delete_driver/<int:id>', methods=['POST'])
@login_required
def delete_driver(id):
    driver = Driver.query.get(id)
    db.session.delete(driver)
    db.session.commit()
    return redirect(url_for('view_drivers'))

# ==== Vehicles ====

@app.route('/vehicles')
@login_required
def view_vehicles():
    vehicles = Vehicle.query.all()
    return render_template('vehicles.html', vehicles=vehicles)

@app.route('/add_vehicle', methods=['POST'])
@login_required
def add_vehicle():
    vehicle = Vehicle(
        registration_number=request.form['registration_number'],
        model=request.form['model'],
        year=request.form['year'],
        owner=request.form['owner'],
        license_expiry=request.form['license_expiry'],
        insurance_expiry=request.form['insurance_expiry'],
        mot_expiry=request.form['mot_expiry'],
        notes=request.form['notes']
    )
    db.session.add(vehicle)
    db.session.commit()
    return redirect(url_for('view_vehicles'))

@app.route('/delete_vehicle/<int:id>', methods=['POST'])
@login_required
def delete_vehicle(id):
    vehicle = Vehicle.query.get(id)
    db.session.delete(vehicle)
    db.session.commit()
    return redirect(url_for('view_vehicles'))

# ==== Τρέξε την εφαρμογή ====

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
