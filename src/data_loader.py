import pandas as pd
import os
import sys


class DataLoader:
    """
    Handles data loading, cleaning, and physical validation for the NASA Airfoil Self-Noise dataset.

    This module serves as the 'Foundation' phase of the project, ensuring that
    the data adheres to aerodynamic physical constraints before modeling.
    """

    def __init__(self, raw_data_path="data/raw/airfoil_self_noise.csv"):
        """
        Initialize the DataLoader.

        Args:
            raw_data_path (str): Path to the raw .dat or .csv file.
                                 Defaults to 'data/raw/airfoil_self_noise.csv'.
        """
        self.raw_data_path = raw_data_path

        # Mapping columns to physical variables based on NASA documentation
        # Units: Hz, Degrees, Meters, m/s, Meters, dB
        self.columns = [
            "Frequency",
            "Angle_of_Attack",
            "Chord_Length",
            "Free_Stream_Velocity",
            "Suction_Side_Displacement_Thickness",
            "Sound_Pressure_Level"
        ]

    def load_raw_data(self):
        """
        Loads the raw dataset and assigns meaningful column names.

        Returns:
            pd.DataFrame: The loaded DataFrame with correct headers, or None if failed.
        """
        if not os.path.exists(self.raw_data_path):
            print(f"[ERROR] Data file not found at: {self.raw_data_path}")
            print("Please check the configured raw_data_path (default: data/raw/airfoil_self_noise.csv).")
            return None

        try:
            # The dataset is typically tab-separated and has no header row.
            df = pd.read_csv(self.raw_data_path, sep='\t', header=None)

            # Verify structure
            if df.shape[1] != 6:
                raise ValueError(f"Expected 6 columns, found {df.shape[1]}. Check the delimiter.")

            df.columns = self.columns
            print(f"[INFO] Raw data loaded successfully. Shape: {df.shape}")
            return df

        except Exception as e:
            print(f"[CRITICAL] Failed to load data: {e}")
            return None

    def validate_physics(self, df):
        """
        Performs 'Physics Consistency Checks' on the data.
        This ensures we are not feeding the model physically impossible values
        (e.g., negative speed or frequency).

        Args:
            df (pd.DataFrame): The dataframe to validate.

        Returns:
            pd.DataFrame: The validated dataframe.
        """
        print("\n--- Starting Aerodynamic Physics Validation ---")

        # Rule 1: Frequency and Velocity must be non-negative
        if (df['Frequency'] < 0).any() or (df['Free_Stream_Velocity'] < 0).any():
            print("[WARNING] Negative Frequency or Velocity detected! This violates physical laws.")
        else:
            print("[PASS] Frequency and Velocity values are valid (non-negative).")

        # Rule 2: Sound Pressure Level (dB) check
        # Typical range is 0-140 dB. Values < 0 or > 160 are suspicious.
        if (df['Sound_Pressure_Level'] > 160).any() or (df['Sound_Pressure_Level'] < 0).any():
            print("[WARNING] Abnormal Sound Pressure Levels (dB) detected.")
        else:
            print("[PASS] Sound Pressure Levels are within a realistic range.")

        # Rule 3: Geometric constraints (Chord length)
        if (df['Chord_Length'] <= 0).any():
            print("[WARNING] Invalid Chord Length (<= 0) detected.")
        else:
            print("[PASS] Geometric features (Chord Length) are valid.")

        print("--- Physics Validation Completed ---\n")
        return df

    def save_processed_data(self, df, save_path="data/processed/airfoil_cleaned.csv"):
        """
        Saves the processed dataframe to the 'processed' directory for the modeling phase.

        Args:
            df (pd.DataFrame): Data to save.
            save_path (str): Destination path.
        """
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        try:
            df.to_csv(save_path, index=False)
            print(f"[INFO] Processed data saved to: {save_path}")
        except Exception as e:
            print(f"[ERROR] Could not save processed data: {e}")


# Module Test (execute this file directly to test Phase 1)
if __name__ == "__main__":
    loader = DataLoader()
    df = loader.load_raw_data()
    if df is not None:
        loader.validate_physics(df)