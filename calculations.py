# calculations.py
from collections import Counter
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from scipy.stats import norm  # For Z-score calculation
import math
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///relative_risk.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class RelativeRiskDB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cancer_type = db.Column(db.String(255), nullable=False)
    medicine_name = db.Column(db.String(255), nullable=False)
    relative_risk = db.Column(db.Float, nullable=False)
    ConfIntervalRR_Lower = db.Column(db.Float, nullable=True)
    ConfIntervalRR_Upper = db.Column(db.Float, nullable=True)

# Create the table in the database
with app.app_context():
    db.create_all()
def insert_initial_values(sql_file_path):
    with sqlite3.connect('instance/relative_risk.db') as conn:
        cursor = conn.cursor()

        # Check if the table already exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('relative_risk_db',))
        table_exists = cursor.fetchone()

    
            # Read SQL file content
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()

        # Execute SQL script to create the table
        cursor.executescript(sql_script)

        # Commit the changes
        conn.commit()


# Path to your InitialDB.sql file
sql_file_path = 'initial_database/InitialDB.sql'

# Call the function to insert initial values
insert_initial_values(sql_file_path)

def insert_into_relative_risk_db(cancer_type, medicine_name, relative_risk, lower_bound, upper_bound):
    with app.app_context():
        new_entry = RelativeRiskDB(
            cancer_type=cancer_type,
            medicine_name=medicine_name,
            relative_risk=relative_risk,
            ConfIntervalRR_Lower=lower_bound,
            ConfIntervalRR_Upper=upper_bound
        )
        db.session.add(new_entry)
        db.session.commit()



def find_most_common_cancer(app, entries):
    with app.app_context():
        # Filter entries with 'have_cancer' set to True
        entries_with_cancer = [entry for entry in entries if entry.have_cancer]

        # Extract cancer types from filtered entries
        cancer_types = [entry.cancerType for entry in entries_with_cancer if entry.cancerType]

        if cancer_types:
            # Use Counter to find the most common cancer type and its count
            most_common_cancer, count = Counter(cancer_types).most_common(1)[0]

            return most_common_cancer, count
        else:
            return None, 0

def find_most_common_medicine(app, entries, most_common_cancer_type):
    with app.app_context():
        # Filter entries with the specified most common cancer type
        entries_with_specific_cancer = [entry for entry in entries if entry.have_cancer and entry.cancerType == most_common_cancer_type]

        if entries_with_specific_cancer:
            # Extract medications from filtered entries
            medications = [medication.strip().upper() for entry in entries_with_specific_cancer for medication in entry.medications.split(',')]

            # Use Counter to find all medicines and their counts
            medicine_counts = Counter(medications)

            # Sort medicines by count in descending order
            sorted_medicines = sorted(medicine_counts.items(), key=lambda x: x[1], reverse=True)

            return sorted_medicines
        else:
            return None

def count_most_common_cancer_without_medicine(app, entries, most_common_cancer_type, most_common_medicine):
    with app.app_context():
        # Filter entries with the specified most common cancer type
        entries_with_specific_cancer = [entry for entry in entries if entry.have_cancer and entry.cancerType == most_common_cancer_type]

        # Filter entries without the most common medicine
        entries_without_medicine = [entry for entry in entries_with_specific_cancer if most_common_medicine not in entry.medications.upper()]

        return len(entries_without_medicine)

def count_most_common_medicine_without_cancer(app, entries, most_common_cancer_type, most_common_medicine):
    with app.app_context():
        # Filter entries with the specified most common medicine
        entries_with_specific_medicine = [entry for entry in entries if most_common_medicine in entry.medications.upper()]

        # Filter entries without the most common cancer type
        entries_without_cancer = [entry for entry in entries_with_specific_medicine if entry.cancerType != most_common_cancer_type]

        return len(entries_without_cancer)

def count_entries_without_common_cancer_and_medicine(app, entries, most_common_cancer_type, most_common_medicine):
    with app.app_context():
        # Filter entries without the most common cancer type
        entries_without_common_cancer = [entry for entry in entries if entry.cancerType != most_common_cancer_type]

        # Filter entries without the most common medicine
        entries_without_common_medicine = [entry for entry in entries if most_common_medicine not in entry.medications.upper()]

        # Find the common entries between the two filtered lists (logical AND)
        entries_without_common_cancer_and_medicine = set(entries_without_common_cancer) & set(entries_without_common_medicine)

        return len(entries_without_common_cancer_and_medicine)
    

def calculate_ci_rr(rr, a, b, c, d, confidence_level=0.95):
    """
    Calculate the confidence interval of the relative risk.

    Parameters:
    - rr: Relative risk
    - a, b, c, d: Counts used in the relative risk calculation
    - confidence_level: Desired confidence level (default is 0.95)

    Returns:
    - Tuple (lower_bound, upper_bound) of the confidence interval
    """
    if (b + a) != 0 and (c + d) != 0 and c != 0:
        z_score = norm.ppf(1 - (1 - confidence_level) / 2)  # Z-score for the desired confidence level

        ln_rr = math.log(rr)
        se_ln_rr = math.sqrt(max(1 / a + 1 / c - 1 / (b + a) - 1 / (d + c), 0))  # Ensure non-negative value

        lower_bound = math.exp(ln_rr - z_score * se_ln_rr)
        upper_bound = math.exp(ln_rr + z_score * se_ln_rr)

        return lower_bound, upper_bound
    else:
        print("Division by zero avoided. Confidence interval calculation skipped.")
        return None, None

def perform_calculations(app, entries):
    with app.app_context():
        all_entries = entries.query.all()
        unique_cancer_types = set(entry.cancerType for entry in all_entries if entry.have_cancer and entry.cancerType)

        # Sort unique cancer types by their count in descending order
        sorted_cancer_types = sorted(unique_cancer_types, key=lambda x: sum(1 for entry in all_entries if entry.have_cancer and entry.cancerType == x), reverse=True)

        for most_common_cancer_type in sorted_cancer_types:
            count_of_most_common_cancer = sum(1 for entry in all_entries if entry.have_cancer and entry.cancerType == most_common_cancer_type)

            # Find all medicines sorted by count in descending order
            sorted_medicines = find_most_common_medicine(app, all_entries, most_common_cancer_type)

            for most_common_medicine_with_cancer_type, A in sorted_medicines:
                B = count_most_common_cancer_without_medicine(app, all_entries, most_common_cancer_type, most_common_medicine_with_cancer_type)
                C = count_most_common_medicine_without_cancer(app, all_entries, most_common_cancer_type, most_common_medicine_with_cancer_type)
                D = count_entries_without_common_cancer_and_medicine(app, all_entries, most_common_cancer_type, most_common_medicine_with_cancer_type)

                # Print the values of each variable
                print("Most Common Cancer Type:", most_common_cancer_type)
                print("Count of Most Common Cancer Type:", count_of_most_common_cancer)
                print("Most Common Medicine with Cancer Type:", most_common_medicine_with_cancer_type)
                print("Count of Most Cancer Type That Took Medicine, A:", A)
                print("Count that took Medicine and did not get Cancer Type, B:", B)
                print("Count that got cancer Type without taking medicine, C:", C)
                print("Count Without Cancer Type and without Medicine, D:", D)
                print(" Relative Risk (RR) = (A / (B + A)) / (C / (C + D))")
                print("Calculating...")

                # Check for division by zero
                if (B + A) != 0 and (C + D) != 0 and C != 0:
                    RR = (A / (B + A)) / (C / (C + D))

                    print("RR:", RR)
                    confidence_interval = calculate_ci_rr(RR, A, B, C, D)
                    print("Confidence Interval:", confidence_interval)
                
                    insert_into_relative_risk_db(most_common_cancer_type, most_common_medicine_with_cancer_type, RR, confidence_interval[0], confidence_interval[1])
                    

    
                else:
                    print("Division by zero avoided. RR calculation skipped.")

def returnCancerName(medName):
    with app.app_context():
        # Query the database to find all entries with the given medicine name
        entries = RelativeRiskDB.query.filter_by(medicine_name=medName).all()

        if entries:
            # Return a list of unique associated cancer types
            unique_cancer_names = list(set(entry.cancer_type for entry in entries))
            return unique_cancer_names
        else:
            return "Exact Cancer Unknown"

