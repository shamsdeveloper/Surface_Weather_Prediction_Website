import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import plotly.express as px
class WeatherPrediction:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None
        self.model = None

    def load_data(self):
        """Load and preprocess the dataset."""
        if not os.path.exists(self.file_path):
            print(f"Error: The file '{self.file_path}' does not exist.")
            new_path = input("Please provide the correct path to the CSV file: ")
            if not os.path.exists(new_path):
                raise FileNotFoundError(f"File not found at '{new_path}'. Please ensure the file exists and try again.")
            self.file_path = new_path

        try:
            self.data = pd.read_csv(self.file_path)
            print("Data loaded successfully!")
            print(self.data.head())
        except FileNotFoundError as e:
            print(f"File not found: {e}")
            raise

        # Fill missing values (adjust based on your data)
        self.data.ffill(inplace=True)
        print("Missing values filled.")

    def feature_engineering(self):
        """Perform feature engineering."""
        # Focus only on the important columns
        self.data = self.data[['temp', 'wave_period', 'wavelength', 'wave_depth', 'day']]
        
        # Ensure that the 'day' column is in datetime format
        self.data['day'] = pd.to_datetime(self.data['day'])

        # Create lag features for weather and wave parameters
        self.data['temp_lag1'] = self.data['temp'].shift(1)
        self.data['wave_period_lag1'] = self.data['wave_period'].shift(1)
        self.data['wavelength_lag1'] = self.data['wavelength'].shift(1)
        self.data['wave_depth_lag1'] = self.data['wave_depth'].shift(1)

        # Drop rows with NaN values after lagging
        self.data.dropna(inplace=True)

        # Define features and labels
        self.features = ['temp_lag1', 'wave_period_lag1', 'wavelength_lag1', 'wave_depth_lag1']
        self.X = self.data[self.features]
        self.y = self.data[['temp', 'wave_period', 'wavelength', 'wave_depth']]
        print("Feature engineering completed!")

    def train_model(self):
        """Train the XGBoost model."""
        # Split data into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)

        # Train an XGBoost model
        self.model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.05, max_depth=6, random_state=42)
        self.model.fit(X_train, y_train)

        # Make predictions
        y_pred = self.model.predict(X_test)

        # Evaluate the model
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        print(f"Model trained successfully! RMSE: {rmse:.2f}, R^2 Score: {r2:.2f}")

        # Save the test set for visualization
        self.X_test = X_test
        self.y_test = y_test
        self.y_pred = y_pred

    def visualize_results(self):
        """Visualize the predictions and feature importance."""
        # Plot actual vs predicted for temperature, wave period, wavelength, and wave depth
        plt.figure(figsize=(10, 6))
        plt.scatter(self.y_test['temp'], self.y_pred[:, 0], alpha=0.6, color='blue')
        plt.plot([self.y_test['temp'].min(), self.y_test['temp'].max()], [self.y_test['temp'].min(), self.y_test['temp'].max()], '--', color='red', linewidth=2)
        plt.title('Actual vs Predicted Temperature')
        plt.xlabel('Actual Temperature')
        plt.ylabel('Predicted Temperature')
        plt.show()

        # Per-day prediction for each parameter
        for i, param in enumerate(['temp', 'wave_period', 'wavelength', 'wave_depth']):
            plt.figure(figsize=(10, 6))
            plt.plot(self.y_test['temp'], self.y_pred[:, i], 'bo', alpha=0.6, label=f'Predicted {param}')
            plt.plot(self.y_test['temp'], self.y_test[param], 'ro', alpha=0.6, label=f'Actual {param}')
            plt.title(f'Actual vs Predicted {param.capitalize()}')
            plt.xlabel('Temperature')
            plt.ylabel(f'{param.capitalize()}')
            plt.legend()
            plt.show()

        # Plot wave properties predictions
        wave_params = ['wave_period', 'wavelength', 'wave_depth']
        plt.figure(figsize=(10, 6))
        for i, param in enumerate(wave_params):
            plt.plot(self.y_test['temp'], self.y_pred[:, i + 1], label=f'Predicted {param}')
        plt.title('Wave Parameters Prediction')
        plt.xlabel('Temperature')
        plt.ylabel('Wave Parameters')
        plt.legend()
        plt.show()

        # Interactive plot for wave parameters over time
        fig = px.line(self.data, x='day', y=['wave_period', 'wavelength', 'wave_depth'], title='Wave Parameters Over Time')
        fig.show()

        # Visualize temperature trend
        fig = px.line(self.data, x='day', y='temp', title='Temperature Trends Over Time')
        fig.show()

    def save_model(self, file_name):
        """Save the trained model to a file."""
        joblib.dump(self.model, file_name)
        print(f"Model saved as {file_name}!")

    def load_model(self, file_name):
        """Load a pre-trained model."""
        self.model = joblib.load(file_name)
        print(f"Model loaded from {file_name}!")

