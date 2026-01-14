import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import joblib
import os
from src.utils import evaluate_model


class ModelTrainer:
    """
    Manages the training, evaluation, and saving of machine learning models.
    Supports:
    1. Linear Regression (Baseline)
    2. XGBoost Regressor (Advanced with Grid Search)
    """

    def __init__(self, df, target_column='Sound_Pressure_Level'):
        """
        Initializes the trainer with the dataset.
        """
        self.df = df
        self.target_column = target_column
        self.model = None
        self.scaler = StandardScaler()
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.best_params = None  # To store XGBoost best params

    def prepare_data(self, test_size=0.2, random_state=42):
        """
        Splits and scales the data.
        """
        print("\n[INFO] Preparing data for training...")

        X = self.df.drop(columns=[self.target_column])
        y = self.df[self.target_column]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        # Scaling is essential for Linear Regression, helpful for XGBoost
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_test_scaled = self.scaler.transform(self.X_test)

        print(f"[INFO] Data Split: Train {self.X_train.shape[0]}, Test {self.X_test.shape[0]}")

    def train_linear_regression(self):
        """
        Trains baseline Linear Regression.
        """
        print("\n>>> Phase 2: Training Linear Regression (Baseline)...")
        self.model = LinearRegression()
        self.model.fit(self.X_train_scaled, self.y_train)
        print("[SUCCESS] Linear Regression model trained.")

    def train_xgboost(self):
        """
        Trains XGBoost Regressor using GridSearchCV for Hyperparameter Tuning.
        This represents Phase 3 (Advanced Modeling).
        """
        print("\n>>> Phase 3: Training XGBoost with Grid Search...")

        # Define the parameter grid to search
        param_grid = {
            'n_estimators': [100, 200, 300],
            'learning_rate': [0.01, 0.1, 0.2],
            'max_depth': [3, 5, 7],
            'subsample': [0.8, 1.0]
        }

        xgb = XGBRegressor(objective='reg:squarederror', random_state=42)

        # 5-Fold Cross Validation
        grid_search = GridSearchCV(
            estimator=xgb,
            param_grid=param_grid,
            cv=5,
            scoring='neg_mean_squared_error',
            verbose=1,
            n_jobs=-1  # Use all CPU cores
        )

        print("[INFO] Starting Hyperparameter Tuning (This may take a moment)...")
        grid_search.fit(self.X_train_scaled, self.y_train)

        # Select the best model
        self.model = grid_search.best_estimator_
        self.best_params = grid_search.best_params_

        print(f"[SUCCESS] Best Parameters Found: {self.best_params}")

    def evaluate(self, model_name="Model"):
        """
        Evaluates the currently trained model.
        """
        if self.model is None:
            print("[ERROR] Model not trained yet!")
            return None

        print(f"[INFO] Evaluating {model_name} on test set...")
        y_pred = self.model.predict(self.X_test_scaled)

        metrics = evaluate_model(self.y_test, y_pred, model_name=model_name)
        return metrics

    def save_model(self, filename):
        """
        Saves the model and scaler.
        """
        if self.model is None:
            return

        save_dir = "models/trained_models"
        os.makedirs(save_dir, exist_ok=True)

        model_path = os.path.join(save_dir, filename)
        joblib.dump(self.model, model_path)

        # Scaler is always overwritten to match the latest training
        scaler_path = os.path.join(save_dir, "scaler.pkl")
        joblib.dump(self.scaler, scaler_path)

        print(f"[INFO] Model saved to: {model_path}")