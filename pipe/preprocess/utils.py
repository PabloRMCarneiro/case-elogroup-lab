import logging
import pandas as pd

def to_snake_case(df: pd.DataFrame) -> None:
    """
    Convert DataFrame column names to snake_case in place.

    The function transforms each column name to lowercase, replaces spaces
    and non-alphanumeric characters with underscores, and adds underscores before
    capital letters when needed.

    Args:
        df (pd.DataFrame): The DataFrame whose columns will be converted.

    Returns:
        None
    """
    df.columns = (
        df.columns.str.replace(r"(?<!^)(?=[A-Z])", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
        .str.replace(" ", "_")
        .str.lower()
    )


def clean_whitespace(df: pd.DataFrame) -> None:
    """
    Strip leading and trailing whitespace from string columns in the DataFrame.

    Iterates over all columns with the object data type and applies the
    string strip method to each.

    Args:
        df (pd.DataFrame): The DataFrame to clean.

    Returns:
        None
    """
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()


def remove_outlier(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Remove outliers from a specified column using the IQR method.

    Computes the first and third quartiles (Q1 and Q3) and removes rows
    where the column value is outside 1.5 times the interquartile range (IQR).

    Args:
        df (pd.DataFrame): Input DataFrame.
        column (str): Column name on which to remove outliers.

    Returns:
        pd.DataFrame: A new DataFrame with outliers removed.
    """
    try:
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)].copy()
    except Exception as e:
        logging.error(f"Error removing outliers from column '{column}': {e}", exc_info=True)
        return df.copy()


def start_data(file_path: str) -> pd.DataFrame:
    """
    Read a CSV file and return a cleaned DataFrame.

    with names starting with 'Unnamed', and drops duplicate rows.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pd.DataFrame: A cleaned DataFrame without duplicate rows.

    Raises:
        ValueError: If an error occurs while reading the CSV file.
    """
    try:
        df = pd.read_csv(file_path, sep=None, engine='python')
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        return df.drop_duplicates()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}", exc_info=True)
        raise ValueError(f"Error reading the file: {e}")


def finish_data(df: pd.DataFrame, output_path: str) -> None:
    """
    Apply post-processing steps and save the DataFrame to a CSV file.

    The function converts column names to snake_case, cleans whitespace in string
    columns, and then saves the DataFrame as a CSV file at the specified location.

    Args:
        df (pd.DataFrame): The DataFrame to be processed.
        output_path (str): The file path where the processed CSV file will be saved.

    Returns:
        None

    Raises:
        Exception: If an error occurs during saving.
    """
    try:
        to_snake_case(df)
        clean_whitespace(df)
        df.to_csv(output_path, index=False)
    except Exception as e:
        logging.error(f"Error saving processed data to {output_path}: {e}", exc_info=True)
        raise


def extract_zcta(df: pd.DataFrame, column: str) -> pd.Series:
    """
    Extract a five-digit ZCTA (zipcode) from a specified column of the DataFrame.

    Uses a regular expression to extract the first occurrence of a 5-digit number.

    Args:
        df (pd.DataFrame): DataFrame containing the column.
        column (str): The name of the column to extract the zip code from.

    Returns:
        pd.Series: A Series containing the extracted zip code.
    """
    return df[column].str.extract(r"(\d{5})")[0]


def specific_processing(df: pd.DataFrame, process_type: str) -> pd.DataFrame:
    """
    Process the DataFrame based on the specified type.

    Supported processing types include:
      - 'demographic'
      - 'economic'
      - 'exams'
      - 'geocode'
      - 'transactional'

    Args:
        df (pd.DataFrame): The input DataFrame to process.
        process_type (str): The processing type to apply.

    Returns:
        pd.DataFrame: The processed DataFrame.

    Raises:
        Exception: Propagates exceptions after logging if processing fails.
    """
    try:
        if process_type == 'demographic':
            # Convert columns beginning with "Population" to numeric.
            num_cols = [col for col in df.columns if col.startswith("Population")]
            df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

            # Extract ZCTA from the 'GeographicAreaName' column.
            df["zipcode"] = extract_zcta(df, 'GeographicAreaName')

            # Remove outliers.
            df = remove_outlier(df, 'SexRatio(males per 100 females)')

            # Drop the original geographic column.
            df.drop(columns=["GeographicAreaName"], inplace=True)

            # Reshape data: melt population columns into a single 'age_group' column.
            df = pd.melt(
                df,
                id_vars=["Id", "zipcode", "TotalPopulation", "SexRatio(males per 100 females)", "MedianAgeInYears"],
                value_vars=num_cols,
                var_name="age_group",
                value_name="group_population"
            )

            # Adjust age group labels for improved readability.
            df["age_group"] = (
                df["age_group"]
                .str.replace("Population_", "", regex=False)
                .str.replace("to", " - ", regex=False)
                .str.replace("Under", "< ", regex=False)
                .str.replace("AndOver", " >=", regex=False)
                .str.replace("Years", " Years", regex=False)
            )

        elif process_type == 'economic':
            # Convert columns that begin with "TotalHouseholds" to numeric.
            num_cols = [col for col in df.columns if col.startswith("TotalHouseholds")]
            df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

            # Extract zipcode from 'Geographic Area Name' and drop the original column.
            df["zipcode"] = extract_zcta(df, 'Geographic Area Name')
            df.drop(columns=["Geographic Area Name"], inplace=True)

            # Reshape data: melt TotalHouseholds columns.
            df = pd.melt(
                df,
                id_vars=["id", "zipcode"],
                value_vars=num_cols,
                var_name="household_range",
                value_name="total_households"
            )

            # Clean the household_range values.
            df["household_range"] = (
                df["household_range"]
                .str.replace("TotalHouseholds_", "", regex=False)
                .str.replace("to", " - ", regex=False)
                .str.replace("LessThan", "< ", regex=False)
                .str.replace("OrMore", " >=", regex=False)
            )

        elif process_type == 'exams':
            # Convert 'CodItem' column to string.
            df["CodItem"] = df["CodItem"].astype(str)

        elif process_type == 'geocode':
            # Remove rows with null zip codes.
            df = df[df["Zipcode"].notnull()]
            df["Zipcode"] = df["Zipcode"].astype(str).str.replace(".0", "", regex=False)

            # Split 'Location' into 'latitude' and 'longitude'.
            df[['latitude', 'longitude']] = df["Location"].str.split(",", expand=True)
            df.drop(columns=["Location"], inplace=True)

            # Split 'Address' into components.
            df[['street', 'city', 'state_zipcode']] = df["Address"].str.split(",", expand=True)
            df[['state', '_zipcode']] = df["state_zipcode"].str.strip().str.split(" ", expand=True)
            df = df.drop(columns=["Address", "state_zipcode", "_zipcode"])


        elif process_type == 'transactional':
            # Convert date columns to datetime.
            df["Date of birth"] = pd.to_datetime(df["Date of birth"], format="%d/%m/%Y %H:%M:%S", errors="coerce")
            df["Date of service"] = pd.to_datetime(df["Date of service"], format="%Y-%m-%d", errors="coerce")

            # Convert testing cost to float (handle comma as the decimal separator).
            df["Testing Cost"] = df["Testing Cost"].str.replace(",", ".").astype(float)

            # Impute missing dates of birth with the median date.
            median_dob = df["Date of birth"].median()
            df["Date of birth"].fillna(median_dob, inplace=True)

            # Remove outliers
            df = remove_outlier(df, 'Date of birth')
            df = remove_outlier(df, 'Testing Cost')

        else:
            logging.warning(f"Unsupported processing type: '{process_type}'. No changes will be applied.")
    except Exception as e:
        logging.error(f"Error during specific_processing for type '{process_type}': {e}", exc_info=True)
        raise

    return df
