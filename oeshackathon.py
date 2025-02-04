# -*- coding: utf-8 -*-
"""OESHackathon.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dPmpE6q1JI-5K53W82oKZNNS8Kwlk1kw
"""

import pandas as pd
import numpy as np


import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, classification_report, confusion_matrix, make_scorer


from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

import warnings
warnings.filterwarnings('ignore')

# Load telemetry data and labels
telemetry_df = pd.read_csv('/content/drive/MyDrive/dataset/telemetry_for_operations_training.csv')
labels_df = pd.read_csv('/content/drive/MyDrive/dataset/operations_labels_training.csv')

telemetry_df.isnull().sum()

labels_df.isnull().sum()

# Convert date columns to datetime format with error handling for mixed formats
telemetry_df['create_dt'] = pd.to_datetime(telemetry_df['create_dt'], errors='coerce', format='mixed')
labels_df['start_time'] = pd.to_datetime(labels_df['start_time'], errors='coerce', format='mixed')
labels_df['end_time'] = pd.to_datetime(labels_df['end_time'], errors='coerce', format='mixed')

# Check for any invalid date conversions
print(telemetry_df['create_dt'].isnull().sum())  # Check how many invalid dates were converted to NaT
print(labels_df['start_time'].isnull().sum())
print(labels_df['end_time'].isnull().sum())

# Sort both dataframes by their respective keys
telemetry_df = telemetry_df.sort_values('create_dt')
labels_df = labels_df.sort_values('start_time')

# Perform the merge_asof operation again after sorting
merged_df = pd.merge_asof(
    telemetry_df,
    labels_df[['start_time', 'end_time', 'operation_kind_id', 'mdm_object_name']],
    left_on='create_dt',
    right_on='start_time',
    by='mdm_object_name',
    direction='backward'
)

# Drop rows where operation_kind_id is missing (if any)
merged_df = merged_df.dropna(subset=['operation_kind_id'])

# Check the shape of the merged dataframe to ensure it's correct
merged_df.shape

merged_df['total_accel'] = (merged_df['accel_forward_nn']**2 + merged_df['accel_braking_nn']**2 +
                            merged_df['accel_angular_nn']**2 + merged_df['accel_vertical_nn']**2)**0.5


merged_df.fillna(0, inplace=True)


X = merged_df.drop(columns=['operation_kind_id', 'create_dt', 'mdm_object_name', 'start_time', 'end_time'])


y = merged_df['operation_kind_id']


X.head()

from sklearn.model_selection import train_test_split

# Split the data into training (80%) and validation (20%) sets
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Check the shape of the training and validation sets
X_train.shape, X_val.shape

from sklearn.ensemble import RandomForestClassifier


# Initialize the Random Forest model with 100 estimators
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

# Train the model on the training set
rf_model.fit(X_train, y_train)

# Predict the operational state on the validation set
y_pred = rf_model.predict(X_val)

from sklearn.metrics import f1_score

# Assuming y_val contains the actual labels and y_pred contains the predicted labels
actual = y_val  # True labels from the validation set
predicted = y_pred  # Predictions from the Random Forest model

# Calculate the weighted F1 score
f1 = f1_score(actual, predicted, average='weighted')

# Final score as per the problem's formula
score = max(0, 100 * f1)

# Print the score
print(f"Final Score: {score:.2f}")

# Check feature importance from the Random Forest model
importances = rf_model.feature_importances_
feature_names = X_train.columns

# Create a DataFrame to visualize feature importance
importances_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': importances
}).sort_values(by='Importance', ascending=False)

# Display the top features
importances_df.head(10)

from sklearn.model_selection import cross_val_score

# Perform cross-validation and get the weighted F1 score for each fold
cv_scores = cross_val_score(rf_model, X, y, cv=5, scoring='f1_weighted')

# Calculate the mean cross-validation score
mean_cv_score = cv_scores.mean()

# Print the cross-validation score
print(f"Cross-Validation F1 Score: {mean_cv_score * 100:.2f}")

# Load the validation telemetry data
validation_df = pd.read_csv('/content/drive/MyDrive/dataset/telemetry_for_operations_validation.csv')

# Display the first few rows of the validation data
validation_df.head()

# Check for missing values in the validation data
validation_df.isnull().sum()

# Perform feature engineering on the validation data (e.g., total_accel)
validation_df['total_accel'] = (validation_df['accel_forward_nn']**2 + validation_df['accel_braking_nn']**2 +
                                validation_df['accel_angular_nn']**2 + validation_df['accel_vertical_nn']**2)**0.5

# Fill missing values (if any)
validation_df.fillna(0, inplace=True)

# Ensure the validation set has the same columns as the training set
X_validation = validation_df.drop(columns=['create_dt', 'mdm_object_name'])  # Keep the necessary features

# Make predictions on the validation data
final_predictions = rf_model.predict(X_validation)

# Prepare the submission file (with 'create_dt', 'mdm_object_name', and 'operation_kind_id')
submission = pd.DataFrame({
    'create_dt': validation_df['create_dt'],
    'mdm_object_name': validation_df['mdm_object_name'],
    'operation_kind_id': final_predictions  # Predicted operational state
})

# Save the submission as a CSV file
submission.to_csv('/content/drive/MyDrive/dataset/final_submission.csv', index=False)

# Print confirmation
print("Final submission file saved as final_submission.csv")

submission.shape

