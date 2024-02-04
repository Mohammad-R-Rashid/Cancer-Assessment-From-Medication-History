import os
import sqlite3

# Check if the database file exists
db_file = 'MedDB.db'
if os.path.exists(db_file):
    print("Database file already exists.")
else:
    # Connect to a new SQLite database file
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Read the SQL file and execute its content to create the table and insert data
    with open('initial_database/MedDB.sql', 'r') as sql_file:
        sql_script = sql_file.read()
        cursor.executescript(sql_script)

    # Commit the changes
    conn.commit()

    # Close the database connection
    conn.close()

    print("New database created.")

# Connect to the existing SQLite database
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Retrieve DrugName column from mytable
cursor.execute('SELECT DrugName FROM mytable')

# Fetch all the DrugName values
drug_names = cursor.fetchall()

# Close the database connection
conn.close()

# Write DrugName values to a text file separated by commas
with open('drug_names.csv', 'w') as file:
    for index, drug_name in enumerate(drug_names):
        # Add comma after each drug name except for the last one
        if index < len(drug_names) - 1:
            file.write(drug_name[0] + ',')
        else:
            # No comma after the last drug name
            file.write(drug_name[0])

print("Drug names exported to 'drug_names.csv'")
