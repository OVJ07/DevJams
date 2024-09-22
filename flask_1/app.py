from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

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
        self.user_credentials = {}

    def add_bicycle(self, reg_number, location):
        if reg_number not in self.bicycles:
            self.bicycles[reg_number] = Bicycle(reg_number, location)

    def register_student(self, student_id, password):
        self.user_credentials[student_id] = password

    def validate_login(self, student_id, password):
        return self.user_credentials.get(student_id) == password

    def rent_bicycle(self, student_id, reg_number):
        # Check if the user already has a rented bicycle
        if any(bike.current_renter == student_id and not bike.is_available for bike in self.bicycles.values()):
            return False  # User already has a rented bicycle

        bicycle = self.bicycles.get(reg_number)
        if bicycle and bicycle.is_available:
            bicycle.is_available = False
            bicycle.current_renter = student_id
            bicycle.rent_time = datetime.now()
            return True
        return False

    def return_bicycle(self, student_id, reg_number, drop_location):
        bicycle = self.bicycles.get(reg_number)
        if bicycle and bicycle.current_renter == student_id:
            rental_duration = datetime.now() - bicycle.rent_time
            rental_minutes = rental_duration.total_seconds() / 60
            rental_fee = rental_minutes * self.rental_rate_per_minute

            self.owed_amounts[student_id] = self.owed_amounts.get(student_id, 0) + rental_fee
            bicycle.is_available = True
            bicycle.current_renter = None
            bicycle.location = drop_location
            return rental_fee, self.owed_amounts[student_id]
        return None

    def get_available_bicycles(self):
        return {reg: bike.location for reg, bike in self.bicycles.items() if bike.is_available}

    def get_rental_history(self, student_id):
        rented_bikes = []
        for reg, bike in self.bicycles.items():
            if bike.current_renter == student_id:
                rented_bikes.append({
                    'reg_number': reg,
                    'rent_time': bike.rent_time,
                    'location': bike.location
                })
        return rented_bikes

rental_system = RentalSystem()

# Add bicycles
for i in range(1, 6):
    rental_system.add_bicycle(f"000{i}", "MGR building")

# Routes
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    student_id = request.form['registrationNumber']
    password = request.form['password']

    # Register new student if not registered
    if student_id not in rental_system.user_credentials:
        rental_system.register_student(student_id, password)
        session['student_id'] = student_id
        return redirect(url_for('dashboard'))

    # Validate login
    if rental_system.validate_login(student_id, password):
        session['student_id'] = student_id
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid credentials, please try again.'

@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('home'))

    student_id = session['student_id']
    available_bikes = rental_system.get_available_bicycles()
    rental_history = rental_system.get_rental_history(student_id)
    amount_due = float(rental_system.owed_amounts.get(student_id, 0))

    return render_template('dashboard.html', 
                           available_bikes=available_bikes, 
                           rental_history=rental_history,
                           amount_due=amount_due)

@app.route('/rent', methods=['POST'])
def rent():
    if 'student_id' not in session:
        return redirect(url_for('home'))

    student_id = session['student_id']
    reg_number = request.form['bicycle']

    if rental_system.rent_bicycle(student_id, reg_number):
        return redirect(url_for('dashboard'))
    else:
        return 'You must return your current bicycle before renting a new one.'

@app.route('/return', methods=['POST'])
def return_bicycle():
    if 'student_id' not in session:
        return redirect(url_for('home'))

    student_id = session['student_id']
    reg_number = request.form['bicycle']
    drop_location = request.form['location']

    result = rental_system.return_bicycle(student_id, reg_number, drop_location)
    if result:
        return redirect(url_for('dashboard'))
    else:
        return 'Failed to return bicycle.'

if __name__ == '__main__':
    app.run(debug=True)