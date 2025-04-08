import logging
import os
import threading
from typing import Dict

from .utils import start_data, finish_data, specific_processing

# Mapping of processing types to raw file identifiers.
PREPROCESS_METADATA: Dict[str, str] = {
    'demographic': 'DemographicData_ZCTAs',
    'economic': 'EconomicData_ZCTAs',
    'exams': 'exams_data',
    'geocode': 'df_geocode',
    'transactional': 'transactional_data'
}


def process_item(key: str, raw: str, raw_dir: str, processed_dir: str) -> None:
    """
    Process a single dataset based on a key.

    This function reads the raw CSV file, applies specific processing for the type,
    then writes the cleaned data to a designated output file. Logging is used to
    trace progress and errors.

    Args:
        key (str): The identifier for the processing type (e.g., 'economic', 'exams').
        raw (str): The raw file identifier (without the .csv extension).
        raw_dir (str): Directory where the raw CSV files are located.
        processed_dir (str): Directory where the processed CSV files will be saved.

    Returns:
        None
    """
    try:
        logging.info(f"Starting preprocessing for dataset '{key.upper()}'.")

        raw_file = os.path.join(raw_dir, f"{raw}.csv")
        df = start_data(file_path=raw_file)

        df = specific_processing(df, key)

        output_path = os.path.join(processed_dir, f"{key}_data_clean.csv")
        finish_data(df, output_path)

        logging.info(f"Preprocessed data for '{key.upper()}' saved to: {output_path}")
    except Exception as e:
        logging.error(f"Error processing dataset '{key.upper()}': {e}", exc_info=True)


def preprocess(raw_dir: str, processed_dir: str) -> None:
    """
    Preprocess all datasets concurrently using threads.

    This function creates and starts a thread for each dataset defined in the metadata,
    then waits for all threads to finish.

    Args:
        raw_dir (str): Directory where the raw CSV files are located.
        processed_dir (str): Directory where the processed CSV files will be stored.

    Returns:
        None
    """
    threads = []

    for key, raw in PREPROCESS_METADATA.items():
        thread = threading.Thread(target=process_item, args=(key, raw, raw_dir, processed_dir))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()
