import os
import logging
from typing import Dict, List

import pandas as pd

# Define constants for datasets and income mapping.
DATA_SETS: List[str] = ['geocode', 'economic', 'demographic']
INCOME_MAPPING: Dict[str, int] = {
    '< $10.000': 5000,
    '$10.000 - $14.999': 12500,
    '$15.000 - $24.999': 20000,
    '$25.000 - $34.999': 30000,
    '$35.000 - $49.999': 42500,
    '$50.000 - $74.999': 62500,
    '$75.000 - $99.999': 87500,
    '$100.000 - $149.999': 125000,
    '$150.000 - $199.999': 175000,
    '$200.000 >=': 250000
}


def load_datasets(processed_dir: str) -> Dict[str, pd.DataFrame]:
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


def select(processed_dir: str) -> pd.DataFrame:
    """
    Select top regions based on a computed expansion indicator.

    This function loads the required processed datasets, computes the weighted average income
    and demographic indicators, and then calculates an expansion indicator defined as the ratio of
    normalized group_population to normalized sex ratio. It returns the top three regions sorted by
    the expansion indicator, excluding regions in the 'Medium-High' income quartile.

    Args:
        processed_dir (str): Directory where the processed CSV files are stored.

    Returns:
        pd.DataFrame: A DataFrame with selected columns including zipcode, total_population,
                      sex ratio, group_population, and income_quartile.
    """
    # Load all the necessary datasets.
    datasets = load_datasets(processed_dir)
    economic_df = datasets.get('economic')
    demographic_df = datasets.get('demographic')

    if economic_df is None or demographic_df is None:
        error_msg = "Required datasets (economic and demographic) are missing."
        logging.error(error_msg)
        raise ValueError(error_msg)

    # Compute weighted income information.
    weighted_income_df = compute_weighted_income(economic_df, INCOME_MAPPING)
    # Compute demographic indicators.
    age_indicator = compute_age_indicator(demographic_df)

    # Select regions with total_population above the 97th quantile.
    population_threshold = age_indicator['total_population'].quantile(0.97)
    age_indicator_top3 = age_indicator[age_indicator['total_population'] > population_threshold]
    logging.info("Filtered regions with total population above the 97th quantile.")

    # Merge demographic information with weighted income data.
    merged_df = age_indicator_top3.merge(weighted_income_df, on='zipcode', how='left')

    # Normalize group population and sex ratio to avoid scale differences.
    merged_df['norm_group_population'] = normalize_series(merged_df['group_population'])
    merged_df['norm_sex_ratio'] = normalize_series(merged_df['sex_ratiomalesper100females'])

    # Compute the expansion indicator as the ratio of normalized group_population
    # to normalized sex ratio, taking care to avoid division by zero.
    merged_df['expansion_indicator'] = merged_df.apply(
        lambda row: row['norm_group_population'] / row['norm_sex_ratio']
        if row['norm_sex_ratio'] != 0 else float('inf'),
        axis=1
    )

    # Sort by expansion indicator in descending order and select the top 3 results.
    final_result = merged_df.sort_values(by='expansion_indicator', ascending=False).head(3)
    final_result = final_result[[
        'zipcode',
        'total_population',
        'sex_ratiomalesper100females',
        'group_population',
        'income_quartile'
    ]]

    logging.info("Selected top regions based on the expansion indicator.")
    
    return final_result
