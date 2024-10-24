import sqlite3
import time
import shutil

# Step 1: Connect to the healthcare database (or create it if it doesn't exist)
conn = sqlite3.connect('healthcare.db')
cur = conn.cursor()

# Create Patients table
cur.execute('''CREATE TABLE IF NOT EXISTS Patients (
                PatientID INTEGER PRIMARY KEY,
                Name TEXT NOT NULL,
                ContactDetails TEXT,
                MedicalHistory TEXT
            )''')

# Create Appointments table
cur.execute('''CREATE TABLE IF NOT EXISTS Appointments (
                AppointmentID INTEGER PRIMARY KEY,
                PatientID INTEGER,
                StaffID INTEGER,
                AppointmentDate TEXT,
                Details TEXT,
                FOREIGN KEY (PatientID) REFERENCES Patients(PatientID)
            )''')

# Create TransactionLog table
cur.execute('''CREATE TABLE IF NOT EXISTS TransactionLog (
                TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                Operation TEXT NOT NULL,
                TableAffected TEXT NOT NULL,
                DataAffected TEXT NOT NULL,
                Timestamp TEXT NOT NULL
            )''')

# Step 2: Define roles and permissions
roles_permissions = {
    "Administrator": ["insert_patient", "insert_appointment", "view_patients", "view_appointments", "edit_patient", "edit_appointment", "delete_patient", "delete_appointment", "backup_database", "restore_database"],
    "MedicalStaff": ["insert_patient", "view_patients", "edit_patient"],
    "AdminStaff": ["view_appointments", "insert_appointment", "edit_appointment", "delete_appointment"]
}

# Step 3: Define passwords for each role
role_passwords = {
    "Administrator": "admin123",  # Example password for Administrator
    "MedicalStaff": "medstaff456",  # Example password for MedicalStaff
    "AdminStaff": "adminstaff789"  # Example password for AdminStaff
}

# Function to log transactions
def log_transaction(operation, table_affected, data_affected):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    try:
        cur.execute("INSERT INTO TransactionLog (Operation, TableAffected, DataAffected, Timestamp) VALUES (?, ?, ?, ?)",
                    (operation, table_affected, data_affected, timestamp))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred while logging the transaction: {e}")

# Function to check if a role has permission for an action
def has_permission(role, action):
    if action in roles_permissions.get(role, []):
        return True
    else:
        print(f"{role} does not have permission to perform {action}")
        return False

# Step 4: Password authentication
def authenticate_role(role):
    password = input(f"Enter password for {role}: ")
    if password == role_passwords.get(role):
        print(f"Authentication successful for {role}")
        return True
    else:
        print(f"Authentication failed for {role}")
        return False

# Step 5: Insert Patients
def insert_patient(patient_id, name, contact, medical_history, user_role):
    if has_permission(user_role, "insert_patient"):
        try:
            cur.execute("INSERT INTO Patients (PatientID, Name, ContactDetails, MedicalHistory) VALUES (?, ?, ?, ?)", 
                        (patient_id, name, contact, medical_history))
            log_transaction('INSERT', 'Patients', f'PatientID={patient_id}, Name={name}, MedicalHistory={medical_history}')
            print("Patient inserted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while inserting patient: {e}")

# Step 6: Insert Appointments
def insert_appointment(appointment_id, patient_id, staff_id, appointment_date, details, user_role):
    if has_permission(user_role, "insert_appointment"):
        try:
            cur.execute("INSERT INTO Appointments (AppointmentID, PatientID, StaffID, AppointmentDate, Details) VALUES (?, ?, ?, ?, ?)", 
                        (appointment_id, patient_id, staff_id, appointment_date, details))
            log_transaction('INSERT', 'Appointments', f'AppointmentID={appointment_id}, PatientID={patient_id}, AppointmentDate={appointment_date}')
            print("Appointment inserted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while inserting appointment: {e}")

# Step 7: View Patients
def view_patients(user_role):
    if has_permission(user_role, "view_patients"):
        try:
            cur.execute("SELECT * FROM Patients")
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred while retrieving patients: {e}")
            return []

# Step 8: View Appointments
def view_appointments(user_role):
    if has_permission(user_role, "view_appointments"):
        try:
            cur.execute("SELECT * FROM Appointments")
            return cur.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred while retrieving appointments: {e}")
            return []

# Step 9: Edit Patient Information
def edit_patient(patient_id, new_name=None, new_contact=None, new_history=None, user_role=None):
    if has_permission(user_role, "edit_patient"):
        try:
            if new_name:
                cur.execute("UPDATE Patients SET Name = ? WHERE PatientID = ?", (new_name, patient_id))
            if new_contact:
                cur.execute("UPDATE Patients SET ContactDetails = ? WHERE PatientID = ?", (new_contact, patient_id))
            if new_history:
                cur.execute("UPDATE Patients SET MedicalHistory = ? WHERE PatientID = ?", (new_history, patient_id))
                log_transaction('UPDATE', 'Patients', f'PatientID={patient_id}, MedicalHistory={new_history}')
            print("Patient information updated successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while editing patient information: {e}")

# Step 10: Edit Appointment Information
def edit_appointment(appointment_id, new_date=None, new_details=None, user_role=None):
    if has_permission(user_role, "edit_appointment"):
        try:
            if new_date:
                cur.execute("UPDATE Appointments SET AppointmentDate = ? WHERE AppointmentID = ?", (new_date, appointment_id))
            if new_details:
                cur.execute("UPDATE Appointments SET Details = ? WHERE AppointmentID = ?", (new_details, appointment_id))
            log_transaction('UPDATE', 'Appointments', f'AppointmentID={appointment_id}, AppointmentDate={new_date}')
            print("Appointment information updated successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while editing appointment information: {e}")

# Step 11: Delete Patients
def delete_patient(patient_id, user_role):
    if has_permission(user_role, "delete_patient"):
        try:
            cur.execute("DELETE FROM Patients WHERE PatientID = ?", (patient_id,))
            log_transaction('DELETE', 'Patients', f'PatientID={patient_id}')
            print("Patient deleted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while deleting patient: {e}")

# Step 12: Delete Appointments
def delete_appointment(appointment_id, user_role):
    if has_permission(user_role, "delete_appointment"):
        try:
            cur.execute("DELETE FROM Appointments WHERE AppointmentID = ?", (appointment_id,))
            log_transaction('DELETE', 'Appointments', f'AppointmentID={appointment_id}')
            print("Appointment deleted successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while deleting appointment: {e}")

# Step 13: Backup the database
def backup_database(user_role):
    if has_permission(user_role, "backup_database"):
        try:
            backup_conn = sqlite3.connect('healthcare_backup.db')
            conn.backup(backup_conn)
            backup_conn.close()
            print("Backup completed successfully.")
        except sqlite3.Error as e:
            print(f"An error occurred while backing up the database: {e}")

# Step 14: Restore the database
def restore_database(user_role):
    if has_permission(user_role, "restore_database"):
        try:
            global conn, cur  # Declare global variables here
            start_time = time.time()  # Start timing the restoration
            conn.close()  # Close the current connection
            
            # Restore the database by copying the backup file
            shutil.copy('healthcare_backup.db', 'healthcare.db')
            
            # Reopen the connection to the restored database
            conn = sqlite3.connect('healthcare.db')
            cur = conn.cursor()
            transition_time = time.time() - start_time  # Calculate the time it took to restore
            print(f"Database restoration completed successfully in {transition_time:.2f} seconds.")
        except sqlite3.Error as e:
            print(f"An error occurred while restoring the database: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Step 15: Replaying Transaction Logs for Restore
def replay_transaction_logs():
    print("Restoring database by replaying transaction logs...")

    try:
        cur.execute("SELECT * FROM TransactionLog")
        logs = cur.fetchall()

        for log in logs:
            transaction_id, operation, table_affected, data_affected, timestamp = log
            print(f"Replaying Transaction {transaction_id}: {operation} on {table_affected} with Data: {data_affected} at {timestamp}")
            # Here we would re-execute the operation based on the log, simulating restoration.

    except sqlite3.Error as e:
        print(f"An error occurred while replaying transaction logs: {e}")

# Step 16: Menu to choose actions
def main_menu():
    # Prompt the user to enter their role
    role = input("Enter your role (Administrator, MedicalStaff, AdminStaff): ")
    if not authenticate_role(role):
        return

    while True:
        print("\nOptions:")
        print("1. Insert Patient")
        print("2. Insert Appointment")
        print("3. View Patients")
        print("4. View Appointments")
        print("5. Edit Patient")
        print("6. Edit Appointment")
        print("7. Delete Patient")
        print("8. Delete Appointment")
        print("9. Backup Database")
        print("10. Restore Database")
        print("11. Replay Transaction Logs")
        print("12. Exit")

        choice = input("Choose an option (1-12): ")

        if choice == '1':
            patient_id = input("Enter Patient ID: ")
            name = input("Enter Patient Name: ")
            contact = input("Enter Contact Details: ")
            medical_history = input("Enter Medical History: ")
            insert_patient(patient_id, name, contact, medical_history, role)
        
        elif choice == '2':
            appointment_id = input("Enter Appointment ID: ")
            patient_id = input("Enter Patient ID: ")
            staff_id = input("Enter Staff ID: ")
            appointment_date = input("Enter Appointment Date (YYYY-MM-DD): ")
            details = input("Enter Appointment Details: ")
            insert_appointment(appointment_id, patient_id, staff_id, appointment_date, details, role)
        
        elif choice == '3':
            patients = view_patients(role)
            for patient in patients:
                print(patient)
        
        elif choice == '4':
            appointments = view_appointments(role)
            for appointment in appointments:
                print(appointment)

        elif choice == '5':
            patient_id = input("Enter Patient ID to edit: ")
            new_name = input("Enter new Name (leave blank to keep current): ")
            new_contact = input("Enter new Contact Details (leave blank to keep current): ")
            new_history = input("Enter new Medical History (leave blank to keep current): ")
            edit_patient(patient_id, new_name or None, new_contact or None, new_history or None, role)
        
        elif choice == '6':
            appointment_id = input("Enter Appointment ID to edit: ")
            new_date = input("Enter new Date (leave blank to keep current): ")
            new_details = input("Enter new Details (leave blank to keep current): ")
            edit_appointment(appointment_id, new_date or None, new_details or None, role)
        
        elif choice == '7':
            patient_id = input("Enter Patient ID to delete: ")
            delete_patient(patient_id, role)

        elif choice == '8':
            appointment_id = input("Enter Appointment ID to delete: ")
            delete_appointment(appointment_id, role)

        elif choice == '9':
            backup_database(role)

        elif choice == '10':
            restore_database(role)

        elif choice == '11':
            replay_transaction_logs()

        elif choice == '12':
            print("Exiting the system.")
            break

        else:
            print("Invalid choice. Please try again.")

# Start the main menu
if __name__ == "__main__":
    main_menu()

# Close the database connection when done
conn.close()
