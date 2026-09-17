"""Regression evidence for the checked-in models, without fitting or tuning."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]


def test_saved_models_reproduce_published_holdout():
    frame = pd.read_csv(ROOT / 'data/processed/airfoil_cleaned.csv')
    X, y = frame.iloc[:, :-1], frame.iloc[:, -1]
    train, test, _, actual = train_test_split(X, y, test_size=.2, random_state=42)
    directory = ROOT / 'models/trained_models'
    scaler = joblib.load(directory / 'scaler.pkl')
    np.testing.assert_allclose(scaler.mean_, train.mean(), rtol=1e-12)
    np.testing.assert_allclose(scaler.var_, train.var(ddof=0), rtol=1e-12)
    assert scaler.n_samples_seen_ == 1202
    evidence = json.loads((ROOT / 'docs/assets/metrics.json').read_text())
    assert test.index.tolist() == evidence['test_indices']
    for name, filename in [('Linear Regression','linear_regression.pkl'), ('XGBoost','xgboost_final.pkl')]:
        prediction = joblib.load(directory / filename).predict(scaler.transform(test))
        observed = [r2_score(actual, prediction), mean_absolute_error(actual, prediction),
                    np.sqrt(mean_squared_error(actual, prediction))]
        expected = [evidence['metrics'][name][key] for key in ['R2','MAE','RMSE']]
        np.testing.assert_allclose(observed, expected, rtol=1e-5, atol=1e-6)
