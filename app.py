from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from calculations import perform_calculations
from regression_model import input_model
from regression_model import mse_2
from calculations import returnCancerName
import sqlite3
import csv
import sqlite3
from flask import jsonify


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Define a model for the data
class MedicationEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    medications = db.Column(db.String, nullable=False)
    have_cancer = db.Column(db.Boolean, nullable=False)
    cancerType = db.Column(db.String, nullable=True)

#Code for the autocomplete dropdown
def fetchDrugNames():
    try:
        drug_names = []
        with open('drug_names.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                drug_names.extend(row)
        return drug_names
    except Exception as e:
        print(f"Error fetching drug names: {e}")
        return []
    
# Create the database tables
with app.app_context():
    db.create_all()
# Drug names will be sent to the HTML
@app.route('/drug_names')
def get_drug_names():
    drug_names = fetchDrugNames()
    return jsonify(drug_names)
@app.route('/')

#Renders home screen
def index():

    return render_template('questions.html')

#Gets the assocaited cancer with medicine name
def get_cancertype_from_database(medname):
    try:
        # Connect to the database
        conn = sqlite3.connect('initial_database/RiskDatabase.db')
        cursor = conn.cursor()

        # Split the input medname by commas to handle multiple keywords
        keywords = medname.split(',')

        # Create a placeholder for the query parameters
        placeholders = ', '.join(['?' for _ in keywords])

        # Build the query dynamically with the appropriate number of placeholders
        query = f"SELECT CancerType FROM mytable WHERE KeyWords IN ({placeholders})"
        
        # Execute the query with the split keywords
        cursor.execute(query, keywords)

        print(f"Querying for medname: {medname}")
        result = cursor.fetchone()
        print(f"Result: {result}")

        # Close the database connection
        conn.close()

        # Return the cancertype if found, otherwise return None
        return result[0] if result else None
    except Exception as e:
        print(f"Error: {e}")
        return None

#This shows what happens when submitted
@app.route('/submit', methods=['POST'])
def submit():
    medications = []
    have_cancer = 'haveCancer' in request.form
    cancerType = request.form.get('cancerType').upper() if 'cancerType' in request.form else None

    # Iterate through submitted medications and checkboxes
    for index, medication in enumerate(request.form.getlist('medications')):
        checkbox_name = f'beforeAfterCancer_{index}'
        prescribed_after_cancer = checkbox_name in request.form

        # Exclude medications prescribed after cancer diagnosis
        if not prescribed_after_cancer:
            medications.append(medication.upper())

    # Check if any medications are present before inserting into the database
    results = []  # List to store medication risk results

    # Check if any medications are present before inserting into the database
    if medications:
        # Create an application context
        with app.app_context():
            # Store the submitted data in the database
            entry = MedicationEntry(medications=', '.join(medications), have_cancer=have_cancer, cancerType=cancerType)
            db.session.add(entry)
            db.session.commit()



            # Check each medication using the model and store the result
            for medication in medications:
                associated_cancer = returnCancerName(medication)
                print("Checked associated cancer")
                result = input_model(medication,associated_cancer)
                print("worked through input model")
                if result is not None:
                    print(f"Result for {medication} (Model 2): {result[0]}")
                
                    results.append({'medication': medication, 'relative_risk': result[0], 'associated_cancer': associated_cancer})
                else:
                    none_result = f"Model 2 result is None for {medication}"
                    print(none_result)

        return render_template('submitted.html', results=results, mse_value=mse_2)  # Render the results template with the data
    else:
        return render_template('submitted.html')  # Add a template for the case when no medications are entered

#Run in debug mode
if __name__ == '__main__':
    app.run(debug=True)
    perform_calculations(app, MedicationEntry)
