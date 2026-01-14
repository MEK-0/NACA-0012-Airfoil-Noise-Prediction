import os
import joblib
import numpy as np
import pytest
import sys

# Add project root to path to ensure imports work if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestModelPipeline:
    """
    Unit Tests for Airfoil Noise Prediction Models.
    Run this using 'pytest' in the terminal.
    """

    @pytest.fixture
    def artifacts(self):
        """Load models and scaler once for all tests."""
        base_path = "models/trained_models"
        try:
            xgb = joblib.load(os.path.join(base_path, "xgboost_final.pkl"))
            lin = joblib.load(os.path.join(base_path, "linear_regression.pkl"))
            scaler = joblib.load(os.path.join(base_path, "scaler.pkl"))
            return xgb, lin, scaler
        except FileNotFoundError:
            pytest.fail("Model files not found. Please run 'main.py' first.")

    def test_artifacts_loading(self, artifacts):
        """Check if models are loaded correctly."""
        xgb, lin, scaler = artifacts
        assert xgb is not None
        assert lin is not None
        assert scaler is not None

    def test_prediction_shape(self, artifacts):
        """Check if model accepts input and returns a float."""
        xgb, _, scaler = artifacts

        # Create a dummy input sample (1 row, 5 features)
        # Random valid values within range
        dummy_input = np.array([[2000, 4.0, 0.22, 39.6, 0.005]])

        # Scale
        dummy_scaled = scaler.transform(dummy_input)

        # Predict
        prediction = xgb.predict(dummy_scaled)

        # Assertions
        assert isinstance(prediction[0], (np.floating, float))
        assert prediction.shape == (1,)

    def test_physical_bounds(self, artifacts):
        """
        Sanity Check:
        Noise level (dB) should be within realistic bounds (e.g., 50dB - 170dB).
        If the model predicts -50dB or 500dB, something is wrong.
        """
        xgb, _, scaler = artifacts

        # Test case: Standard flight condition
        sample = np.array([[1000, 5.0, 0.15, 50.0, 0.004]])
        sample_scaled = scaler.transform(sample)

        pred = xgb.predict(sample_scaled)[0]

        print(f"Test Prediction: {pred:.2f} dB")
        assert 50 < pred < 170, f"Prediction {pred} dB is out of physical bounds!"