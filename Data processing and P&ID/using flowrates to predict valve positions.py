import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Step 1: Read the Excel file and prepare data
excel_file = "CW Loop Test Data.xlsx"
data = pd.read_excel(excel_file)

features = data.iloc[2:7201,[12, 15, 17]]
targets = ['FIC 106 Output Value (FCV 116 Position)','FIC 201 Output Value (FCV 201 Position)','FIC 401 Output Value (FCV 401 Position)']

# Prompt the user to input three numerical values
input_values = []
for i in range(3):
    value = float(input(f"Enter flowrate {i+1}: "))
    input_values.append(value)

# Create a DataFrame with feature names
input_df = pd.DataFrame(data=[input_values], columns=features.columns)

test_value = input_df.values

# Prepare input features and output target
for target in targets:
    X = features
    y = data[target].iloc[2:7201]

    # Step 2: Train-test split and model training
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Predict the output for the user-input data
    manual_input = model.predict(test_value)
    pred_value = target + ": " + str(manual_input[0])
    print(pred_value)
    
    # Predict the output for test data
    predictions = model.predict(X_test)
    manual_input = model.predict(test_value)
    pred_value = target + ": " + str(manual_input)
    print(pred_value)

    # Step 3: Calculate evaluation metrics and plot
    mse = mean_squared_error(y_test, predictions)
    r_squared = r2_score(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    # Create scatter plot
    plt.figure()
    plt.scatter(y_test, predictions, color='green', label=f'Predicted vs Real {target}')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], color='blue', linestyle='--', label='Ideal Fit')
    plt.xlabel(f'Real {target}')
    plt.ylabel(f'Predicted {target}')
    plt.title(f'{target}, R-squared = {r2:.4f}')
    plt.legend()