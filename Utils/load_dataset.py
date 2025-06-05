import pandas as pd
import numpy as np


def load_dataset(file_path: str) -> pd.DataFrame:
    """
    Load a dataset from a CSV file and preprocess it.

    Args:
        file_path (str): Path to the CSV file containing the dataset.

    Returns:
        pd.DataFrame: Preprocessed dataset.
    """
    # Load the dataset
    dataset = pd.read_csv(file_path)

    # Convert 'NDVI_Data' column from string representation of matrices to numpy matrices objects
    dataset["NDVI_Data"] = dataset["NDVI_Data"].apply(lambda x: x.replace("null", "None"))
    dataset["NDVI_Data"] = dataset["NDVI_Data"].apply(eval)
    dataset["NDVI_Data"] = dataset["NDVI_Data"].apply(lambda x: np.array(x))

    # Convert 'Valid_NDVI_Data' column from string representation of lists to numpy arrays
    dataset["Valid_NDVI_Data"] = dataset["Valid_NDVI_Data"].apply(eval)
    dataset["Valid_NDVI_Data"] = dataset["Valid_NDVI_Data"].apply(lambda x: np.array(x))

    # Convert 'Date' column to datetime format
    dataset["Acquisition_Date"] = pd.to_datetime(dataset["Acquisition_Date"], format="%Y-%m-%d")

    return dataset


if __name__ == "__main__":
    # Example usage:
    dataset = load_dataset('../Satellite_NDVI_data_construction.csv')
    print(dataset.head())
    print(dataset.dtypes)
    print(type(dataset.loc[0, "NDVI_Data"]))
