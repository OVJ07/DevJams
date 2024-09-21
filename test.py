from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Bicycle Rental System

class Bicycle:
    def __init__(self, reg_number, location):
        self.reg_number = reg_number
        self.is_available = True
        self.current_renter = None
        self.rent_time = None
        self.location = location

class RentalSystem:
    def __init__(self):
        self.bicycles = {}
        self.rental_rate_per_minute = 1
        self.owed_amounts = {}
        self.user_credentials = {}  # Store student credentials

    def add_bicycle(self, reg_number, location):
        if reg_number not in self.bicycles:
            self.bicycles[reg_number] = Bicycle(reg_number, location)
        else:
            print(f"Bicycle {reg_number} already exists.")

    def register_student(self, student_id, password):
        if student_id not in self.user_credentials:
            self.user_credentials[student_id] = password
        else:
            print(f"Student {student_id} is already registered.")

    def validate_login(self, student_id, password):
        return self.user_credentials.get(student_id) == password

    def rent_bicycle(self, student_reg_number, reg_number):
        if reg_number in self.bicycles:
            bicycle = self.bicycles[reg_number]
            if bicycle.is_available:
                bicycle.is_available = False
                bicycle.current_renter = student_reg_number
                bicycle.rent_time = datetime.now()
                if student_reg_number not in self.owed_amounts:
                    self.owed_amounts[student_reg_number] = 0
                return f"Bicycle {bicycle.reg_number} rented successfully."
            else:
                return f"Bicycle {bicycle.reg_number} is not available."
        else:
            return f"Bicycle {reg_number} does not exist."

    def return_bicycle(self, reg_number, student_reg_number, drop_location):
        if reg_number in self.bicycles:
            bicycle = self.bicycles[reg_number]
            if bicycle.current_renter == student_reg_number:
                rental_duration = datetime.now() - bicycle.rent_time
                rental_minutes = rental_duration.total_seconds() / 60
                rental_fee = rental_minutes * self.rental_rate_per_minute
                self.owed_amounts[student_reg_number] += rental_fee
                bicycle.is_available = True
                bicycle.current_renter = None
                bicycle.rent_time = None
                bicycle.location = drop_location
                return f"Bicycle {reg_number} returned. Total fee: ₹{rental_fee:.2f}."
            else:
                return "This bicycle is not rented by you."
        else:
            return f"Bicycle {reg_number} does not exist."

    def check_availability(self):
        available_bicycles = {k: v for k, v in self.bicycles.items() if v.is_available}
        return available_bicycles


rental_system = RentalSystem()
rental_system.add_bicycle("0001", "MGR building")
rental_system.add_bicycle("0002", "MGR building")
rental_system.add_bicycle("0003", "MGR building")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    registration_number = request.form['registrationNumber']
    password = request.form['password']

    # Check if the student is registered and the password is correct
    if rental_system.validate_login(registration_number, password):
        session['student_id'] = registration_number
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid login credentials. <a href="/">Try again</a>', 401

@app.route('/register', methods=['POST'])
def register():
    registration_number = request.form['registrationNumber']
    password = request.form['password']

    rental_system.register_student(registration_number, password)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('home'))

    student_id = session['student_id']
    bicycles = rental_system.check_availability()
    return render_template('dashboard.html', bicycles=bicycles, student_id=student_id)

@app.route('/rent', methods=['POST'])
def rent_bicycle():
    if 'student_id' not in session:
        return redirect(url_for('home'))

    student_id = session['student_id']
    reg_number = request.form['reg_number']
    message = rental_system.rent_bicycle(student_id, reg_number)
    return redirect(url_for('dashboard'))

@app.route('/return', methods=['POST'])
def return_bicycle():
    if 'student_id' not in session:
        return redirect(url_for('home'))

    student_id = session['student_id']
    reg_number = request.form['reg_number']
    drop_location = request.form['drop_location']
    message = rental_system.return_bicycle(reg_number, student_id, drop_location)
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('student_id', None)
    return redirect(url_for('home'))

if __name__ == '_main_':
    app.run(debug=True)