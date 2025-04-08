import os
import logging
from typing import Dict, List

import pandas as pd

def load_datasets(processed_dir: str, DATA_SETS: List) -> Dict[str, pd.DataFrame]:
    """
    Load cleaned datasets from the processed directory.

    Args:
        processed_dir (str): Directory where the processed CSV files are stored.

    Returns:
        Dict[str, pd.DataFrame]: A dictionary mapping dataset names to their respective DataFrames.

    Raises:
        FileNotFoundError: If any required CSV file is not found.
    """
    datasets = {}
    for dataset in DATA_SETS:
        file_path = os.path.join(processed_dir, f"{dataset}_data_clean.csv")
        try:
            df = pd.read_csv(file_path)
            datasets[dataset] = df
            logging.info(f"Loaded dataset '{dataset.upper()}' from {file_path}.")
        except Exception as e:
            logging.error(f"Failed to load dataset '{dataset.upper()}' from {file_path}: {e}", exc_info=True)
            raise FileNotFoundError(f"Unable to load dataset '{dataset}' from {file_path}") from e
    return datasets


def compute_weighted_income(economic_df: pd.DataFrame, income_mapping: Dict[str, int]) -> pd.DataFrame:
    """
    Compute the weighted average income by zipcode from the economic dataset.

    Args:
        economic_df (pd.DataFrame): The economic dataset DataFrame.
        income_mapping (Dict[str, int]): Mapping of income ranges to numeric values.

    Returns:
        pd.DataFrame: DataFrame with columns 'zipcode', 'weighted_avg_income', and 'income_quartile'.
    """
    df = economic_df.copy()
    # Map income values to numeric values using the provided mapping.
    df['income_value'] = df['household_range'].map(income_mapping)
    # Calculate weighted average income by zipcode.
    weighted_income = df.groupby('zipcode').apply(
        lambda x: (x['income_value'] * x['total_households']).sum() / x['total_households'].sum()
    )
    weighted_income_df = weighted_income.reset_index()
    weighted_income_df.columns = ['zipcode', 'weighted_avg_income']

    # Divide weighted income into quartiles.
    quartile_labels = ['Q1 (Low)', 'Q2 (Medium-Low)', 'Q3 (Medium-High)', 'Q4 (High)']
    weighted_income_df['income_quartile'] = pd.qcut(
        weighted_income_df['weighted_avg_income'], q=4, labels=quartile_labels
    )
    # Exclude the 'Medium-High' quartile (Q3)
    weighted_income_df = weighted_income_df[weighted_income_df['income_quartile'] != 'Q3 (Medium-High)']

    logging.info("Computed weighted income and assigned income quartiles.")
    return weighted_income_df


def compute_age_indicator(
    demographic_df: pd.DataFrame, 
    age_groups: List[str] = None
) -> pd.DataFrame:
    """
    Compute demographic indicators from the demographic dataset.

    This function filters the data for prioritized age groups and aggregates relevant statistics by zipcode.

    Args:
        demographic_df (pd.DataFrame): The demographic dataset DataFrame.
        age_groups (List[str], optional): List of age groups to prioritize.
            Defaults to ['25 - 34 Years', '35 - 44 Years', '45 - 54 Years'].

    Returns:
        pd.DataFrame: A DataFrame with aggregated indicators such as total population,
                      sex ratio, median age, and sum of group population by zipcode.
    """
    if age_groups is None:
        age_groups = ['25 - 34 Years', '35 - 44 Years', '45 - 54 Years']

    filtered_demo = demographic_df[demographic_df['age_group'].isin(age_groups)]
    age_indicator = filtered_demo.groupby('zipcode').agg({
        'total_population': 'first',
        'sex_ratiomalesper100females': 'first',
        'median_age_in_years': 'first',
        'group_population': 'sum'
    }).reset_index()

    logging.info("Aggregated demographic indicators from the demographic dataset.")
    return age_indicator


def normalize_series(series: pd.Series) -> pd.Series:
    """
    Normalize a pandas Series to the [0, 1] range using min-max scaling.

    Args:
        series (pd.Series): The series to normalize.

    Returns:
        pd.Series: Normalized series with values between 0 and 1.
    """
    min_val = series.min()
    max_val = series.max()
    if max_val - min_val == 0:
        # Avoid division by zero; return series unchanged or zeros if appropriate.
        return series
    return (series - min_val) / (max_val - min_val)
