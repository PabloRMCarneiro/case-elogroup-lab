import os
import argparse
import logging
import warnings
from pandas.errors import SettingWithCopyWarning

from pipe.preprocess.main import preprocess
from pipe.select.main import select

def main() -> None:
    """
    Orchestrate the execution of the preprocessing and selection pipeline steps.

    This function parses command-line arguments to execute the preprocessing step,
    the selection step, or both. It sets up logging and warning filters, ensures
    necessary directories exist, and calls the respective pipeline modules.
    
    The two available options are:
      --preprocess : Executes the preprocessing for all datasets.
      --select     : Executes the selection of ZCTAs for laboratory expansion.
    
    Returns:
        None
    """
    # Configure logging with a specific format and INFO level.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    
    # Suppress specific warnings from pandas.
    warnings.filterwarnings("ignore", category=SettingWithCopyWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    
    # Set up the command-line argument parser.
    parser = argparse.ArgumentParser(
        description="Pipeline to automate the preprocessing, analysis, and selection of ZCTAs for laboratory expansion."
    )
    parser.add_argument(
        "--preprocess",
        action="store_true",
        help="Execute the preprocessing steps."
    )
    parser.add_argument(
        "--select",
        action="store_true",
        help="Execute the selection of ZCTAs for expansion."
    )
    args = parser.parse_args()

    # Define directories for raw and processed data.
    raw_dir: str = os.path.join("data", "raw")
    processed_dir: str = os.path.join("data", "processed_pipe")

    # Ensure the processed directory exists; create it if necessary.
    if not os.path.exists(processed_dir):
        try:
            os.makedirs(processed_dir)
            logging.info(f"Created processed data directory: {processed_dir}")
        except Exception as e:
            logging.error(f"Failed to create processed directory '{processed_dir}': {e}", exc_info=True)
            raise

    # Run the preprocessing step if requested.
    if args.preprocess:
        logging.info("Starting preprocessing of all datasets...")
        try:
            preprocess(raw_dir, processed_dir)
            logging.info("Preprocessing completed successfully.")
        except Exception as e:
            logging.error("An error occurred during preprocessing.", exc_info=True)

    # Run the selection step if requested.
    if args.select:
        logging.info("Starting selection of ZCTAs for expansion...")
        try:
            result_df = select(processed_dir)
            print(result_df)
            logging.info("Selection of ZCTAs completed successfully.")
        except Exception as e:
            logging.error("An error occurred during the selection process.", exc_info=True)

if __name__ == "__main__":
    main()
