import pandas as pd
import numpy as np
from Utils.load_dataset import load_dataset

def threshold_ndvi_data(dataset: pd.DataFrame, lower_ndvi_threshold: float, upper_ndvi_threshold: float):
    """
    Apply NDVI thresholding to classify pixels into Green, Yellow, and Red categories.

    Args:
        dataset (pd.DataFrame): Pandas DataFrame containing NDVI data.
        lower_ndvi_threshold (float): Lower threshold for NDVI classification.
        upper_ndvi_threshold (float): Upper threshold for NDVI classification.

    Returns:
        pd.DataFrame: Thresholded dataset with classified NDVI pixel counts.
    """
    # Apply thresholding and return numpy arrays
    dataset["Green_NDVI_Pixels"] = dataset["Valid_NDVI_Data"].apply(
        lambda x: np.array([val for val in x if val > upper_ndvi_threshold]))

    dataset["Yellow_NDVI_Pixels"] = dataset["Valid_NDVI_Data"].apply(
        lambda x: np.array([val for val in x if lower_ndvi_threshold < val <= upper_ndvi_threshold]))

    dataset["Red_NDVI_Pixels"] = dataset["Valid_NDVI_Data"].apply(
        lambda x: np.array([val for val in x if val <= lower_ndvi_threshold]))

    # Compute pixel counts
    dataset["Green_NDVI_Pixels_Number"] = dataset["Green_NDVI_Pixels"].apply(len)
    dataset["Yellow_NDVI_Pixels_Number"] = dataset["Yellow_NDVI_Pixels"].apply(len)
    dataset["Red_NDVI_Pixels_Number"] = dataset["Red_NDVI_Pixels"].apply(len)

    return dataset

"""
# Example usage:
dataset = load_dataset('../Satellite_NDVI_data_construction.csv')
columns_to_print = ['Primary_Key', 'Acquisition_Date', 'Valid_NDVI_Data']
print(dataset[columns_to_print])
print(dataset.dtypes)
print("Thresholding")
result_dataset = threshold_ndvi_data(dataset, lower_ndvi_threshold=0.3, upper_ndvi_threshold=0.55)
print(result_dataset[columns_to_print+['Green_NDVI_Pixels']])
print(result_dataset.dtypes)
"""

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
"""