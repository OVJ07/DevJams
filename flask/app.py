from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import random
import string

app = Flask(__name__)

# Bicycle class to represent a single bicycle
class Bicycle:
    def __init__(self, reg_number, location):
        self.reg_number = reg_number
        self.is_available = True
        self.current_renter = None
        self.rent_time = None
        self.location = location

# RentalSystem class to manage the entire rental process
class RentalSystem:
    def __init__(self):
        self.bicycles = {}  # Dictionary of bicycles
        self.user_credentials = {}  # Registered users

    # Add a bicycle to the system
    def add_bicycle(self, reg_number, location):
        if reg_number not in self.bicycles:
            self.bicycles[reg_number] = Bicycle(reg_number, location)
    
    # Register a new user
    def register_student(self, student_id, password):
        self.user_credentials[student_id] = password

    # Validate login credentials
    def validate_login(self, student_id, password):
        return self.user_credentials.get(student_id) == password

    # Check if student is registered
    def is_registered(self, student_id):
        return student_id in self.user_credentials

    # Rent a bicycle to a user
    def rent_bicycle(self, student_id, reg_number):
        bicycle = self.bicycles.get(reg_number)
        if bicycle and bicycle.is_available:
            bicycle.is_available = False
            bicycle.current_renter = student_id
            bicycle.rent_time = datetime.now()
            return bicycle.reg_number  # Bicycle successfully rented
        return None

    # Return a rented bicycle
    def return_bicycle(self, reg_number):
        bicycle = self.bicycles.get(reg_number)
        if bicycle and not bicycle.is_available:
            last_renter = bicycle.current_renter  # Save the renter before resetting
            bicycle.is_available = True
            bicycle.current_renter = None
            bicycle.rent_time = None
            return last_renter  # Return the ID of the last renter
        return None

# Initialize the rental system and add bicycles and their locations
rental_system = RentalSystem()
rental_system.add_bicycle("0001", "MGR building")
rental_system.add_bicycle("0002", "Library")
rental_system.add_bicycle("0003", "Canteen")

# Helper function to generate a random password
def generate_password(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# Route for the home/login page
@app.route('/')
def index():
    return render_template('index.html')

# Handle user login submissions
@app.route('/login', methods=['POST', 'GET'])
def login():
    student_id = request.form['registrationNumber']
    password = request.form.get('password')  # Fetch the password if it exists
    
    # Check if the user is registered
    if rental_system.is_registered(student_id):
        # If registered, validate the credentials
        if rental_system.validate_login(student_id, password):
            print(f"Student {student_id} logged in successfully.")
            return redirect(url_for('dashboard', student_id=student_id))
        else:
            return "Invalid credentials. Please try again.", 401
    else:
        # If not registered, generate a password, register the user, and show the password
        generated_password = generate_password()
        rental_system.register_student(student_id, generated_password)
        return f"Account created. Your password is: {generated_password}. Please login with this password."

# Route to display the dashboard showing available bicycles
@app.route('/dashboard/<student_id>')
def dashboard(student_id):
    available_bicycles = [bicycle for bicycle in rental_system.bicycles.values() if bicycle.is_available]
    print(f"Dashboard loaded for student_id={student_id}")
    return render_template('dashboard.html', student_id=student_id, bicycles=available_bicycles)

# Handle bicycle renting
@app.route('/rent/<student_id>/<reg_number>')
def rent(student_id, reg_number):
    rented_bike = rental_system.rent_bicycle(student_id, reg_number)
    if rented_bike:
        return redirect(url_for('dashboard', student_id=student_id))
    else:
        return "Bicycle not available or error occurred.", 400

# Handle bicycle returning
@app.route('/return/<student_id>/<reg_number>')
def return_bike(student_id, reg_number):
    last_renter = rental_system.return_bicycle(reg_number)
    if last_renter:
        return redirect(url_for('dashboard', student_id=student_id))
    else:
        return "Error in returning bicycle.", 400

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    student_id = request.form['registrationNumber']
    password = request.form['password']
    rental_system.register_student(student_id, password)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
