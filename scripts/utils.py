import pandas as pd

def to_snake_case(df: pd.DataFrame) -> None:
    """
    Convert column names of a DataFrame to snake_case.

    This function modifies the DataFrame in place, transforming its column names
    to snake_case by replacing spaces with underscores, removing non-alphanumeric
    characters, and converting to lowercase.

    Args:
        df (pd.DataFrame): The DataFrame whose column names will be transformed.

    Returns:
        None
    """
    df.columns = (
        df.columns.str.replace(r"(?<!^)(?=[A-Z])", "_", regex=True)
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "", regex=True)
        .str.lower()
    )

def clean_whitespace(df: pd.DataFrame) -> None:
    """
    Remove leading and trailing whitespace from string columns in a DataFrame.

    This function applies the `str.strip()` method to all columns of type `object`
    in the given DataFrame, leaving other column types unchanged.

    Args:
        df (pd.DataFrame): The DataFrame to clean.

    Returns:
        pd.DataFrame: A new DataFrame with whitespace removed from string columns.
    """
    df.apply(lambda col: col.str.strip() if col.dtypes == "object" else col)

def remove_outlier(df: pd.DataFrame, column: str) -> None:
    """
    Remove outliers from a specified column in a DataFrame using the IQR method.

    This function modifies the DataFrame in place by removing rows where the
    specified column's values are considered outliers based on the Interquartile Range (IQR).

    Args:
        df (pd.DataFrame): The DataFrame from which to remove outliers.
        column (str): The name of the column to check for outliers.

    Returns:
        None
    """
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    df.drop(df[(df[column] < lower_bound) | (df[column] > upper_bound)].index, inplace=True)
