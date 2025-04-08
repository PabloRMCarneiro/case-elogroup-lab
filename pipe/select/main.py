import logging
from typing import Dict, List

import pandas as pd

from .utils import load_datasets, compute_weighted_income, compute_age_indicator, normalize_series

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
    datasets = load_datasets(processed_dir, DATA_SETS)
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
