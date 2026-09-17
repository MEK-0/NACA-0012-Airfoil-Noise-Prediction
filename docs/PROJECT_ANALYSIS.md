# Project analysis

## Scope and evidence

Audit of the original commit `80c63c2`. Inspected every tracked source file, both notebooks (code, stored text and plot outputs), both datasets, four serialized artifacts, the dashboard screenshot, requirements and Git history. The original working tree was clean. No CI, Pages configuration, license, training log, dependency lockfile or live application URL was present. This report separates source-code evidence from artifact verification; no model was retrained.

## Repository overview and architecture

- `data/raw/airfoil_self_noise.csv`: headerless, tab-separated data despite the extension.
- `data/processed/airfoil_cleaned.csv`: the same 1,503 numeric rows with column names; no actual cleaning is performed.
- `src/data_loader.py`: load, assign six column names, print basic physical warnings, save data.
- `src/model_trainer.py`: split, standardize, fit linear regression, tune XGBoost, evaluate and persist.
- `src/utils.py`: MAE, RMSE and R² calculations.
- `main.py`: orchestration; upgrades to XGBoost when baseline R² is below 0.85.
- `models/trained_models/`: final XGBoost, linear regression and separate scaler. `linear_regression_baseline.pkl` is byte-identical to `linear_regression.pkl`; preserved for compatibility.
- `app/app.py`: Streamlit sliders, shared scaler and two model predictions.
- `tests/test_model.py`: three smoke tests for artifact loading, output shape and a broad prediction range.
- `notebooks/`: EDA and full-dataset model comparison with embedded plots.
- `assets/dashboard_preview.png`: historical Streamlit screenshot, not a deployment record.

## Dataset

The local dataset has 1,503 rows, five predictors, one target, no missing values and no exact duplicate rows. Raw and processed values match. Dataset origin and units are corroborated by [UCI Airfoil Self-Noise](https://archive.ics.uci.edu/dataset/291/airfoil+self+noise), DOI [10.24432/C5VW2C](https://doi.org/10.24432/C5VW2C). UCI describes NASA wind-tunnel experiments on NACA 0012 airfoils with fixed span and observer position. A byte-level comparison to a newly downloaded original dataset was not performed.

| Repository column | Meaning / unit | Observed range |
| --- | --- | --- |
| Frequency | Frequency, Hz | 200–20,000 |
| Angle_of_Attack | Angle of attack, degrees | 0–22.2 |
| Chord_Length | Chord length, m | 0.0254–0.3048 |
| Free_Stream_Velocity | Free-stream velocity, m/s | 31.7–71.3 |
| Suction_Side_Displacement_Thickness | Suction-side displacement thickness, m | 0.000400682–0.0584113 |
| Sound_Pressure_Level | Scaled sound pressure level, dB (target) | 103.380–140.987 |

## ML workflow and evaluation methodology

1. Load tab-separated data and print checks on frequency, velocity, chord and target. Validation warns; it neither rejects nor cleans rows. Missing values and thickness are not validated.
2. Random 80/20 split using `random_state=42`: 1,202 training and 301 test rows.
3. Fit `StandardScaler` on training predictors, transform training and test data. The scaler is persisted separately. Tree models do not require this scaling, but inference must preserve the saved representation.
4. Fit ordinary least squares `LinearRegression` as baseline.
5. If baseline R² < 0.85, run XGBoost squared-error regression, seed 42, with five-fold `GridSearchCV`, scored by negative MSE. Grid: estimators 100/200/300, learning rate .01/.1/.2, depth 3/5/7, subsample .8/1: 54 combinations, 270 CV fits plus final refit.
6. Report holdout MAE, RMSE and R² and persist final estimator and scaler.

The scaler is fitted before CV, so validation-fold statistics enter scaling within CV (though not the holdout). A future sklearn Pipeline would fit preprocessing separately within each fold. Random rows can share aerodynamic configurations across train and test; the evaluation does not establish transfer to unseen experimental conditions. No grouped split, external validation, uncertainty estimate, stored CV results or split manifest existed.

## Original claims and issues

- README reports linear R² .5583, MAE 3.67, RMSE 4.70 and XGBoost R² .9620, MAE .89, RMSE 1.38. These are historical rounded claims; see the artifact verification below for independently recomputed values.
- Notebook 2 predicts **all** rows, including training observations. Its metrics and plots are descriptive full-data results, not holdout estimates. The website uses fresh holdout plots without overwriting the notebook.
- EDA prose claims a positive thickness–target correlation; the data must be used to check this sign. Correlation does not establish physical causation.
- Notebook feature-importance prose asserts frequency is dominant without deriving the narrative from the sorted values. Verified importances should take precedence.
- Original app interprets predicted noise as aerodynamic stress, efficiency and optimal operating conditions without measurements or validation of those quantities. These descriptions are unsupported.
- Requirements were completely unpinned; pickle metadata identifies sklearn 1.6.1 and XGBoost 3.0.2. Original notebooks used Python 3.9.25. The complete original environment cannot be reconstructed from the repository alone.
- README clone command embeds Markdown inside a shell command and contains `your-username` and an obsolete directory name.
- App and tests resolve artifacts from the working directory. Notebook paths assume execution from `notebooks/`. Training commands must run from the project root.
- App uses externally hosted images; remote availability is not guaranteed. Original screenshot is historical.
- There is no standalone reusable inference module, CI workflow, source license or live Streamlit deployment evidence. Three tests provide smoke coverage, not comprehensive scientific validation.
- `.gitignore` lacks `.venv/`, pytest and plotting caches. Some imports are unused; cosmetic cleanup is lower priority than preserving the pipeline.

## Strengths

Clear module boundaries, a genuine baseline comparison, deterministic split and estimator seed, training-only holdout scaling, explicit tuning grid, persisted artifacts, an operational Python UI and automated smoke tests. Data and notebooks are checked in, allowing independent inspection.

## Recommendations and technical debt

Prioritize transparent holdout evidence, accurate documentation and a static showcase. Preserve the original notebooks, data and artifacts. Add a repeatable evaluation/figure script with artifact hashes and environment versions. Improve artifact path resolution and correct unsupported app text without modifying predictions. Future work: grouped evaluation, fold-local preprocessing, portable model export, pinned full training environment, inference service, SHAP or permutation analysis, uncertainty estimates and tests for invalid input. Select a source-code license explicitly as repository owner; do not assume one.

## Deployment constraints and demo decision

GitHub Pages serves static files and cannot execute the Python app or pickle artifacts. `docs/` contains a self-contained HTML/CSS/JavaScript site with relative asset links and `.nojekyll`; no Node or build step is required. A client-side tree evaluator would require an export, float32/scaling parity checks and maintenance of another inference implementation. The repository contains no browser-ready model or runtime. Use a clearly labeled prediction interface preview, with no simulated predictions, and retain real inference in Streamlit. No live demo link is shown because none is recorded. Pages activation remains a repository setting, not a verified deployment.

## Verification record

The following section is populated from saved-artifact evaluation after the initial repository inspection. See `assets/metrics.json` for full precision, artifact hashes and package versions, and `VALIDATION.md` for final checks.

### Saved-artifact findings

The reconstructed holdout reproduces the historical R² and RMSE. Linear Regression: R² **0.5582979755**, MAE **3.6724145642 dB**, RMSE **4.7041091950 dB**. XGBoost: R² **0.9619923766**, MAE **0.8991173071 dB**, RMSE **1.3799014044 dB**. The original 0.89 MAE claim is imprecise, not evidence of a different model. Correct two-decimal rounding is 0.90. RMSE reduction relative to baseline is approximately 70.7%.

The saved scaler has 1,202 samples and its mean and variance match the reconstructed training subset. This supports split consistency, though the original training log is absent. The final estimator contains 300 trees with depth 7, learning rate 0.1, subsample 0.8, seed 42 and squared-error objective. The repository cannot independently prove that these were the optimal CV settings because the original search results are not stored.

Normalized average gain: thickness **35.99%**, chord **29.84%**, frequency **18.93%**, angle **7.84%**, velocity **7.39%**. This contradicts the notebook’s frequency-first narrative. Thickness–target Pearson correlation is **−0.31267**, contradicting its positive-correlation prose. The regenerated charts and website describe the measured values without causal interpretation.

Initial tests failed because the host lacked `libomp`, before any prediction could execute. Installing the OpenMP runtime resolved that environment failure. The original three tests pass with two existing sklearn warnings about unnamed array inputs. The final validation record includes additional regression checks.

### Implemented scope

Added the static study, five evidence charts, metrics JSON, a read-only artifact evaluation script, static validation, deployment instructions and rewritten README. Fixed app/test artifact paths, a stale loader error message and the removed Streamlit image-width keyword; replaced unsupported app stress/efficiency text. Added an artifact-compatible requirements overlay and ignored local environment/cache outputs. Preserved the training algorithm, all datasets, every model artifact and both notebooks.
