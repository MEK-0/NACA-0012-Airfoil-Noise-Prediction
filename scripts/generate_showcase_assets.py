"""Evaluate saved artifacts and regenerate static evidence; never fits a model.

Run from any working directory with the project requirements installed.
The original holdout is reconstructed from the seed and split in ModelTrainer.
"""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import os
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('MPLCONFIGDIR', str(ROOT / '.mplconfig'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from src.data_loader import DataLoader

ASSETS = ROOT / 'docs' / 'assets'
NAMES = ['Frequency', 'Angle of attack', 'Chord length', 'Free-stream velocity', 'Displacement thickness']
INK, ACCENT, PAPER = '#252b29', '#387563', '#faf9f5'


def save(fig, name):
    fig.savefig(ASSETS / name, dpi=160, bbox_inches='tight', facecolor=PAPER)
    plt.close(fig)


def main():
    ASSETS.mkdir(parents=True, exist_ok=True)
    frame = DataLoader(str(ROOT / 'data/raw/airfoil_self_noise.csv')).load_raw_data()
    if frame is None:
        raise RuntimeError('Cannot load source data')
    X, y = frame.iloc[:, :-1], frame.iloc[:, -1]
    train, test, _, actual = train_test_split(X, y, test_size=.2, random_state=42)
    directory = ROOT / 'models/trained_models'
    scaler = joblib.load(directory / 'scaler.pkl')
    # Guard the reconstructed split against a mismatched saved scaler.
    np.testing.assert_allclose(scaler.mean_, train.mean(axis=0), rtol=1e-12)
    np.testing.assert_allclose(scaler.var_, train.var(axis=0, ddof=0), rtol=1e-12)
    assert scaler.n_samples_seen_ == len(train)
    models = {name: joblib.load(directory / file) for name, file in [
        ('Linear Regression', 'linear_regression.pkl'), ('XGBoost', 'xgboost_final.pkl')]}
    predictions = {name: model.predict(scaler.transform(test)) for name, model in models.items()}
    metrics = {name: {'R2': float(r2_score(actual, pred)),
                      'MAE': float(mean_absolute_error(actual, pred)),
                      'RMSE': float(np.sqrt(mean_squared_error(actual, pred)))}
               for name, pred in predictions.items()}
    importance = dict(zip(X.columns, map(float, models['XGBoost'].feature_importances_)))
    files = list(directory.glob('*.pkl')) + [ROOT / 'data/raw/airfoil_self_noise.csv', ROOT / 'data/processed/airfoil_cleaned.csv']
    report = {'method': 'Saved artifacts; reconstructed random 80/20 holdout; seed 42; no retraining',
              'train_rows': len(train), 'test_rows': len(test), 'test_indices': test.index.tolist(),
              'scaler_matches_training_statistics': True, 'metrics': metrics,
              'feature_importance_type': 'normalized average gain', 'feature_importance': importance,
              'parameters': {k: models['XGBoost'].get_params()[k] for k in ['n_estimators', 'learning_rate', 'max_depth', 'subsample', 'random_state', 'objective']},
              'target_correlations': frame.corr().iloc[:-1, -1].to_dict(),
              'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
              'environment': {'python': platform.python_version(), **{p: importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','xgboost','matplotlib','joblib']}}}
    (ASSETS / 'metrics.json').write_text(json.dumps(report, indent=2) + '\n')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'text.color': INK,
                         'axes.labelcolor': INK, 'axes.edgecolor': '#c7cdc7',
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.facecolor': PAPER, 'figure.facecolor': PAPER,
                         'xtick.color': INK, 'ytick.color': INK, 'svg.hashsalt': 'airfoil'})
    fig, ax = plt.subplots(figsize=(7, 4.4), layout='constrained')
    ax.hist(y, bins=28, color=ACCENT, edgecolor=PAPER)
    ax.set(xlabel='Scaled sound pressure level (dB)', ylabel='Number of observations')
    save(fig, 'target-distribution.png')
    fig, ax = plt.subplots(figsize=(7, 5.5), layout='constrained')
    corr = frame.corr().to_numpy()
    im = ax.imshow(corr, cmap='BrBG', vmin=-1, vmax=1)
    labels = ['Frequency', 'Angle', 'Chord', 'Velocity', 'Thickness', 'Target']
    ax.set_xticks(range(6), labels, rotation=35, ha='right'); ax.set_yticks(range(6), labels)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f'{corr[i,j]:.2f}', ha='center', va='center', color='white' if abs(corr[i,j])>.65 else INK)
    fig.colorbar(im, ax=ax, shrink=.8, label='Pearson correlation')
    save(fig, 'correlations.png')
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout='constrained')
    for ax, (name, pred) in zip(axes, predictions.items()):
        ax.scatter(actual, pred, s=17, alpha=.65, color=ACCENT if name=='XGBoost' else '#887459', linewidths=0)
        ax.plot([100,145], [100,145], '--', color='#6a716d', lw=1)
        ax.set(xlim=(100,145), ylim=(100,145), xlabel='Measured level (dB)', ylabel='Predicted level (dB)', title=name)
        ax.set_aspect('equal'); ax.grid(alpha=.15)
    save(fig, 'predicted-vs-actual.png')
    fig, ax = plt.subplots(figsize=(10, 4.4), layout='constrained')
    ax.scatter(predictions['XGBoost'], actual-predictions['XGBoost'], s=20, alpha=.65, color=ACCENT, linewidths=0)
    ax.axhline(0, color='#6a716d', ls='--', lw=1)
    ax.set(xlabel='Predicted scaled sound pressure level (dB)', ylabel='Residual: measured − predicted (dB)')
    ax.grid(alpha=.15); save(fig, 'residuals.png')
    fig, ax = plt.subplots(figsize=(9, 4.2), layout='constrained')
    order = np.argsort(list(importance.values()))
    values = np.array(list(importance.values()))[order]
    ax.barh(np.array(NAMES)[order], values, color=ACCENT, height=.55)
    for i,v in enumerate(values): ax.text(v+.004, i, f'{v:.1%}', va='center', fontsize=10)
    ax.set(xlabel='Normalized average gain', xlim=(0, max(values)*1.25))
    save(fig, 'feature-importance.png')
    print(json.dumps({k:v for k,v in report.items() if k not in ['test_indices','sha256']}, indent=2))


if __name__ == '__main__':
    main()
