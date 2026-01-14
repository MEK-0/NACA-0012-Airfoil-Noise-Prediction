from src.data_loader import DataLoader
from src.model_trainer import ModelTrainer
import sys


def main():
    print("==================================================")
    print("   AIRFOIL NOISE PREDICTION PROJECT - PIPELINE    ")
    print("==================================================\n")

    # --- PHASE 1: FOUNDATION ---
    # Update: Using .csv as per your file format
    loader = DataLoader(raw_data_path="data/raw/airfoil_self_noise.csv")
    df = loader.load_raw_data()

    if df is None:
        sys.exit("[CRITICAL] Process terminated due to data loading failure.")

    df = loader.validate_physics(df)
    loader.save_processed_data(df)

    # Initialize Trainer
    trainer = ModelTrainer(df, target_column='Sound_Pressure_Level')
    trainer.prepare_data()

    # --- PHASE 2: BENCHMARKING (Linear Regression) ---
    trainer.train_linear_regression()
    metrics_lr = trainer.evaluate(model_name="Linear Regression")
    trainer.save_model("linear_regression.pkl")

    # Decision Logic
    print("\n--------------------------------------------------")
    print(">>> DECISION POINT")
    if metrics_lr['R2'] < 0.85:
        print(f"   [INSIGHT] Baseline R² ({metrics_lr['R2']:.4f}) is below threshold.")
        print("   [ACTION] Triggering Phase 3: Advanced Modeling (XGBoost).")

        # --- PHASE 3: THE UPGRADE (XGBoost) ---
        trainer.train_xgboost()
        metrics_xgb = trainer.evaluate(model_name="XGBoost Regressor")
        trainer.save_model("xgboost_final.pkl")

        # Comparison Report
        improvement = metrics_xgb['R2'] - metrics_lr['R2']
        print(f"\n>>> FINAL REPORT:")
        print(f"   Baseline R² : {metrics_lr['R2']:.4f}")
        print(f"   XGBoost R²  : {metrics_xgb['R2']:.4f}")
        print(f"   Improvement : +{improvement:.4f} ({improvement / metrics_lr['R2'] * 100:.1f}%)")
        print("   [CONCLUSION] Model successfully upgraded to professional standards.")

    else:
        print("   [RESULT] Baseline model is sufficient (Unexpected for this dataset).")


if __name__ == "__main__":
    main()