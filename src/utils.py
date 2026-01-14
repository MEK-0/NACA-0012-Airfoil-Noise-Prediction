from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import numpy as np


def evaluate_model(y_true, y_pred, model_name="Model"):
    """
    Calculates and prints performance metrics (MAE, RMSE, R2).

    Args:
        y_true (array-like): True target values.
        y_pred (array-like): Predicted values by the model.
        model_name (str): Name of the model for logging purposes.

    Returns:
        dict: A dictionary containing MAE, RMSE, and R2 scores.
    """
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    print(f"--- Performance Metrics for: {model_name} ---")
    print(f"   [MAE]  Mean Absolute Error : {mae:.4f}")
    print(f"   [RMSE] Root Mean Sq. Error : {rmse:.4f}")
    print(f"   [R²]   R-Squared Score     : {r2:.4f}")
    print("-" * 50)

    return {"MAE": mae, "RMSE": rmse, "R2": r2}