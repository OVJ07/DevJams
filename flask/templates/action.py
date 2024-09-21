import csv
import os
from datetime import datetime

# File paths
STUDENT_FILE = 'students.csv'
BICYCLE_FILE = 'bicycles.csv'
RENTAL_FILE = 'rentals.csv'

# Initialize CSV files
def init_files():
    if not os.path.exists(STUDENT_FILE):
        with open(STUDENT_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'password'])

    if not os.path.exists(BICYCLE_FILE):
        with open(BICYCLE_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['reg_number', 'is_available', 'current_renter', 'rent_time', 'location'])

    if not os.path.exists(RENTAL_FILE):
        with open(RENTAL_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['rental_id', 'reg_number', 'student_id', 'rental_start', 'rental_end', 'fee'])

class Bicycle:
    def _init_(self, reg_number, location):
        self.reg_number = reg_number
        self.is_available = True
        self.current_renter = None
        self.rent_time = None
        self.location = location

class RentalSystem:
    def _init_(self):
        self.rental_rate_per_minute = 1
        self.load_data()

    def load_data(self):
        # Load students
        self.students = {}
        with open(STUDENT_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.students[row['student_id']] = row['password']

        # Load bicycles
        self.bicycles = {}
        with open(BICYCLE_FILE, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.bicycles[row['reg_number']] = Bicycle(row['reg_number'], row['location'])
                self.bicycles[row['reg_number']].is_available = row['is_available'] == 'True'
                self.bicycles[row['reg_number']].current_renter = row['current_renter'] or None
                self.bicycles[row['reg_number']].rent_time = row['rent_time'] or None

    def save_data(self):
        # Save students
        with open(STUDENT_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['student_id', 'password'])
            for student_id, password in self.students.items():
                writer.writerow([student_id, password])

        # Save bicycles
        with open(BICYCLE_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['reg_number', 'is_available', 'current_renter', 'rent_time', 'location'])
            for bicycle in self.bicycles.values():
                writer.writerow([bicycle.reg_number, bicycle.is_available, bicycle.current_renter, bicycle.rent_time, bicycle.location])

    def add_bicycle(self, reg_number, location):
        if reg_number not in self.bicycles:
            self.bicycles[reg_number] = Bicycle(reg_number, location)
            self.save_data()
            print(f"Bicycle {reg_number} added to the system at location '{location}'.")
        else:
            print(f"Bicycle {reg_number} already exists.")

    def register_student(self, student_id, password):
        if student_id not in self.students:
            self.students[student_id] = password
            self.save_data()
            print(f"Student {student_id} registered successfully.")
        else:
            print(f"Student {student_id} is already registered.")

    def validate_login(self, student_id, password):
        return self.students.get(student_id) == password

    def rent_bicycle(self, student_id):
        available_bicycles = [bicycle for bicycle in self.bicycles.values() if bicycle.is_available]

        if not available_bicycles:
            print("No bicycles available for rent.")
            return

        print("Available bicycles:")
        for i, bicycle in enumerate(available_bicycles, start=1):
            print(f"{i}. Bicycle {bicycle.reg_number} - Location: {bicycle.location}")

        choice = int(input("Select a bicycle by number: ")) - 1

        if 0 <= choice < len(available_bicycles):
            bicycle = available_bicycles[choice]
            bicycle.is_available = False
            bicycle.current_renter = student_id
            bicycle.rent_time = datetime.now().isoformat()

            self.save_data()
            print(f"Bicycle {bicycle.reg_number} rented to student {student_id} at {bicycle.rent_time}.")
        else:
            print("Invalid choice. Please try again.")

    def return_bicycle(self, reg_number, student_id, drop_location):
        if reg_number in self.bicycles:
            bicycle = self.bicycles[reg_number]
            if bicycle.current_renter == student_id:
                rental_duration = datetime.now() - datetime.fromisoformat(bicycle.rent_time)
                rental_minutes = rental_duration.total_seconds() / 60
                rental_fee = rental_minutes * self.rental_rate_per_minute

                with open(RENTAL_FILE, mode='a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([len(open(RENTAL_FILE).readlines()), reg_number, student_id, bicycle.rent_time, datetime.now().isoformat(), rental_fee])

                bicycle.is_available = True
                bicycle.current_renter = None
                bicycle.rent_time = None
                bicycle.location = drop_location

                self.save_data()
                print(f"Bicycle {reg_number} returned at {drop_location}. Rental fee: ₹{rental_fee:.2f}")
            else:
                print(f"You cannot return Bicycle {reg_number} as it is not rented to you.")
        else:
            print(f"Bicycle {reg_number} does not exist in the system.")

    def check_availability(self):
        print("Current status of bicycles:")
        for bicycle in self.bicycles.values():
            status = "available" if bicycle.is_available else f"rented out to {bicycle.current_renter} since {bicycle.rent_time}"
            print(f"Bicycle {bicycle.reg_number}: {status} - Location: {bicycle.location}")
        print()  # New line for better readability

# Initialize rental system
init_files()
rental_system = RentalSystem()

# Add bicycles with locations
rental_system.add_bicycle("0001", "MGR building")
rental_system.add_bicycle("0002", "MGR building")
rental_system.add_bicycle("0003", "MGR building")
rental_system.add_bicycle("0004", "MGR building")
rental_system.add_bicycle("0005", "MGR building")

# User interaction loop
while True:
    student_id = input("Enter your registration number: ").strip()

    if rental_system.validate_login(student_id, input("Enter your password: ").strip()):
        print("Login successful!")
        rental_system.check_availability()

        while True:
            command = input("Enter command (rent/return_bicycle/logout): ").strip().lower()
            if command == 'rent':
                rental_system.rent_bicycle(student_id)
            elif command == 'return_bicycle':
                reg_number = input("Enter the bicycle registration number to be returned: ").strip()
                drop_location = input("Enter the drop-off location: ").strip()
                rental_system.return_bicycle(reg_number, student_id, drop_location)
            elif command == 'logout':
                print("Logging out...")
                break
            else:
                print("Invalid command. Please try again.")
    else:
        password = input("You are not registered. Please create a password: ").strip()
        rental_system.register_student(student_id, password)