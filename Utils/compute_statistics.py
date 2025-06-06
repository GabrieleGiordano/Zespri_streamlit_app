import pandas as pd
import numpy as np
from Utils.load_dataset import load_dataset
from Utils.threshold_dataset import threshold_ndvi_data


def compute_ndvi_statistics(dataset: pd.DataFrame):
    """
    Computes the mean and standard deviation for NDVI pixel categories.

    Args:
        dataset (pd.DataFrame): Pandas DataFrame containing Green, Yellow, and Red NDVI pixel lists.

    Returns:
        pd.DataFrame: Dataset with computed mean and standard deviation for each NDVI pixel category.
    """

    def array_mean(arr):
        return np.mean(arr) if arr.any() else None

    def array_std(arr):
        return np.std(arr, ddof=0) if arr.any() else None  # Using population standard deviation

    # Compute mean
    dataset["Mean_Green_Pixels"] = dataset["Green_NDVI_Pixels"].apply(array_mean)
    dataset["Mean_Yellow_Pixels"] = dataset["Yellow_NDVI_Pixels"].apply(array_mean)
    dataset["Mean_Red_Pixels"] = dataset["Red_NDVI_Pixels"].apply(array_mean)

    # Compute standard deviation
    dataset["Std_Green_Pixels"] = dataset["Green_NDVI_Pixels"].apply(array_std)
    dataset["Std_Yellow_Pixels"] = dataset["Yellow_NDVI_Pixels"].apply(array_std)
    dataset["Std_Red_Pixels"] = dataset["Red_NDVI_Pixels"].apply(array_std)

    return dataset


if __name__ == "__main__":
    # Example usage:
    dataset = load_dataset("../Satellite_NDVI_data_construction.csv")
    thresholded_dataset = threshold_ndvi_data(dataset, lower_ndvi_threshold=0.3, upper_ndvi_threshold=0.55)
    print(dataset.columns)  # Check initial columns

    result_dataset = compute_ndvi_statistics(dataset)
    print(result_dataset.head())
    print(result_dataset.columns)  # Check the new columns added
    print(dataset.dtypes)
    print(dataset["Mean_Green_Pixels"])

"""
KPIN                                    int64
Block_Name                              int64
Primary_Key                            object
Orchard_Name                           object
Acquisition_Date               datetime64[ns]
Year                                    int64
Month                                   int64
Week                                    int64
Day                                     int64
Country_Name                           object
Supply_Area_Name                       object
Supply_Region_Name                     object
Total_Hectares                        float64
Variety_Name                           object
NDVI_Data                              object
Valid_NDVI_Data                        object
Number_Of_Valid_Pixels                  int64
Cloud_Or_Shadow_Percentage              int64
Cloud_Or_Shadow_Return_Code             int64
Green_NDVI_Pixels                      object
Yellow_NDVI_Pixels                     object
Red_NDVI_Pixels                        object
Green_NDVI_Pixels_Number                int64
Yellow_NDVI_Pixels_Number               int64
Red_NDVI_Pixels_Number                  int64
Mean_Green_Pixels                     float64
Mean_Yellow_Pixels                    float64
Mean_Red_Pixels                       float64
Std_Green_Pixels                      float64
Std_Yellow_Pixels                     float64
Std_Red_Pixels                        float64
"""
