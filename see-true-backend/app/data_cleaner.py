import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Column mapping
COLUMN_MAPPING = {
    "timestamp": "timestamp",
    "gazepoint_x": "gazepoint_x",
    "gazepoint_y": "gazepoint_y",
    "pupil_area_(right)_sq_mm": "pupil_area_right_sq_mm",
    "pupil_area_(left)_sq_mm": "pupil_area_left_sq_mm",
    "eye_event": "eye_event"
}

def clean_data(file_path: str) -> pd.DataFrame:
    """
    Clean and preprocess the uploaded CSV data from a file path.
    """
    logger.info(f"Starting data cleaning for file: {file_path}")

    # Step 1: Load the CSV file
    df = pd.read_csv(file_path, delimiter=';', skipinitialspace=True, on_bad_lines='skip')
    logger.info(f"Initial DataFrame shape: {df.shape}")

    # Step 2: Normalize column names
    df.columns = df.columns.str.strip().str.replace(',', '').str.replace(' ', '_').str.lower()
    df = df.rename(columns={col: COLUMN_MAPPING[col] for col in df.columns if col in COLUMN_MAPPING})
    logger.info(f"Normalized and renamed columns: {df.columns.tolist()}")

    # Step 3: Retain only the relevant columns
    relevant_columns = list(COLUMN_MAPPING.values())
    df = df[[col for col in relevant_columns if col in df.columns]]
    logger.info(f"DataFrame shape after keeping necessary columns: {df.shape}")

    # Step 4: Replace NaN values in `eye_event` with 'NA'
    if "eye_event" in df.columns:
        df["eye_event"] = df["eye_event"].fillna("NA")

    # Step 5: Log raw pupil area values
    for col in ["pupil_area_right_sq_mm", "pupil_area_left_sq_mm"]:
        if col in df.columns:
            logger.info(f"Raw values in {col}: {df[col].describe()}")

    # Step 6: Exclude `pupil_area_left_sq_mm` if it contains all zeros
    if "pupil_area_left_sq_mm" in df.columns and df["pupil_area_left_sq_mm"].nunique() == 1 and df["pupil_area_left_sq_mm"].iloc[0] == 0:
        df = df.drop(columns=["pupil_area_left_sq_mm"])
        logger.warning("Excluded `pupil_area_left_sq_mm` column as it contains all zeros.")

    # Step 7: Handle outliers or large values in `pupil_area_left_sq_mm`
    if "pupil_area_left_sq_mm" in df.columns:
        # Apply threshold for outlier handling
        max_allowed_value = 1000  # Example threshold for pupil_area_left_sq_mm
        df["pupil_area_left_sq_mm"] = df["pupil_area_left_sq_mm"].apply(lambda x: min(x, max_allowed_value))
        logger.info(f"Applied threshold to `pupil_area_left_sq_mm` to cap values above {max_allowed_value}.")

    # Step 8: Normalize pupil area columns if they exist
    scaler = MinMaxScaler(feature_range=(0, 1))
    for col in ["pupil_area_right_sq_mm", "pupil_area_left_sq_mm"]:
        if col in df.columns:
            if df[col].nunique() > 1:  # Check if there's more than one unique value
                df[col] = scaler.fit_transform(df[[col]]).round(2)
                logger.info(f"Normalized values in {col}: {df[col].describe()}")
            else:
                logger.warning(f"Skipped normalization for {col} as all values are identical.")

    # Step 9: Strip white spaces in all string columns
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    logger.info("Stripped white spaces from all string values in the DataFrame.")

    # Step 10: Convert 'timestamp' from milliseconds to seconds and normalize
    if "timestamp" in df.columns:
        logger.info("Converting 'timestamp' from milliseconds to seconds.")

        # Convert 'timestamp' from milliseconds to seconds
        df["seconds"] = df["timestamp"] / 1000

        # Create 'chunk' column for grouping into 9-second chunks
        df["chunk"] = (df["seconds"] // 9).astype(int)

        # Normalize timestamp within each chunk
        df["timestamp"] = df.groupby("chunk")["seconds"].transform(lambda x: ((x - x.min()) % 9 + 1).astype(int))

        # Drop the 'seconds' and 'chunk' columns after processing
        df = df.drop(columns=["seconds", "chunk"])
        logger.info("Normalized 'timestamp' and dropped unnecessary columns.")

    logger.info(f"Final DataFrame shape after cleaning: {df.shape}")
    return df
