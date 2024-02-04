import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor, plot_tree
from sklearn.metrics import mean_squared_error
from sklearn.tree import export_text
import matplotlib.pyplot as plt
import numpy as np


# Step 1: Connect to the second SQLite database
db_path = "instance/relative_risk.db"
conn = sqlite3.connect(db_path)

# Query the data from the second table
query = "SELECT medicine_name, cancer_type, relative_risk FROM relative_risk_db;"
df = pd.read_sql_query(query, conn)

# Create a list of dictionaries to hold data for each combination of medication and cancer type
data_rows = []
for _, row in df.iterrows():
    data_rows.append({'medicine_name': row['medicine_name'], 'cancer_type': row['cancer_type'], 'relative_risk': row['relative_risk']})

# Create a new DataFrame from the list of dictionaries
new_df = pd.DataFrame(data_rows)

# One-hot encode the 'medicine_name' and 'cancer_type' columns
X = pd.get_dummies(new_df[['medicine_name', 'cancer_type']])
y = new_df['relative_risk']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Train the Decision Tree regression model for the second database
model = DecisionTreeRegressor()
#model = DecisionTreeRegressor(max_depth=5)  # Limit the depth to 5 for testing purposes 
model.fit(X_train, y_train)

# Make predictions on test data for the second database
predictions = model.predict(X_test)

# Evaluate the model using mean squared error for the second database
mse_2 = mean_squared_error(y_test, predictions)


def input_model(medInputModel, cancerInputModel):
    print("Medication:", medInputModel)
    print("Cancer Type(s):", cancerInputModel)
    
    # Convert medication name and cancer type into a DataFrame with one-hot encoding
    cancer_types = []  # List to store one-hot encoded values for cancer types
    for cancer_type in cancerInputModel:
        cancer_types.append(cancer_type)
    # Create a DataFrame with one-hot encoded values for medication and cancer types
    new_input = pd.get_dummies(pd.DataFrame({'medicine_name': [medInputModel]*len(cancer_types), 'cancer_type': cancer_types}))
    
    # Ensure the columns in new_input match the columns used during training and in the correct order for the model
    new_input = new_input.reindex(columns=X_test.columns, fill_value=0)
    
    print("New Input DataFrame:")
    print(new_input)
    
    # Make prediction using the trained model
    new_prediction = model.predict(new_input)
    print("New Prediction:", new_prediction)
    
    return new_prediction

#input_model("INSULIN", "ALL")


tree_rules = export_text(model, feature_names=list(X.columns))
print(tree_rules)
# Close the connection to the second database
# Visualize the decision tree
"""
plt.figure(figsize=(10, 10))
plot_tree(model, filled=True, feature_names=X.columns, rounded=True, fontsize=9)
plt.show()
"""
# Save the graph as an image file
plt.figure(figsize=(10, 6))
plt.scatter(y_test, predictions, color='blue', alpha=0.5)
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], '--k', lw=2)  # Diagonal line
plt.xlabel('True Values')
plt.ylabel('Predictions')
plt.title('True Values vs. Predictions')
plt.savefig('static/predictions_plot.png')  # Save the plot as an image file
plt.close()  # Close the plot to free up memory

print(f"Mean Squared Error for the second database: {mse_2}")


def calculate_variance(model, X_data, y_data):
    # Make predictions using the provided model
    predictions = model.predict(X_data)
    
    # Calculate the mean of the predicted values
    mean_prediction = predictions.mean()
    
    # Calculate the variance using the formula
    variance = ((predictions - mean_prediction) ** 2).sum() / (len(y_data) - 1)
    
    return variance



conn.close()