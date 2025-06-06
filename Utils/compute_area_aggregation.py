import pandas as pd
import numpy as np

from Utils.load_dataset import load_dataset
from Utils.threshold_dataset import threshold_ndvi_data
from Utils.compute_statistics import compute_ndvi_statistics
from Utils.mean_weekly_resampling import resample_and_average_weekly

def compute_weighted_average(dataset):
    # Group by Year, Month, and Day

    weighted_avg_dataset = dataset.groupby(["Year", "Week"]).agg({
        "Green_NDVI_Pixels_Number": 'sum',
        "Yellow_NDVI_Pixels_Number": 'sum',
        "Red_NDVI_Pixels_Number": 'sum',
        "Mean_Green_Pixels": lambda x: (
            (x * dataset.loc[x.index, "Green_NDVI_Pixels_Number"]).sum() /
            dataset.loc[x.index, "Green_NDVI_Pixels_Number"].sum()
            if dataset.loc[x.index, "Green_NDVI_Pixels_Number"].sum() > 0 else np.nan
        ),
        "Mean_Yellow_Pixels": lambda x: (
            (x * dataset.loc[x.index, "Yellow_NDVI_Pixels_Number"]).sum() /
            dataset.loc[x.index, "Yellow_NDVI_Pixels_Number"].sum()
            if dataset.loc[x.index, "Yellow_NDVI_Pixels_Number"].sum() > 0 else np.nan
        ),
        "Mean_Red_Pixels": lambda x: (
            (x * dataset.loc[x.index, "Red_NDVI_Pixels_Number"]).sum() /
            dataset.loc[x.index, "Red_NDVI_Pixels_Number"].sum()
            if dataset.loc[x.index, "Red_NDVI_Pixels_Number"].sum() > 0 else np.nan
        )
    }).reset_index()

    #
    weighted_avg_dataset["Year_Week"] = pd.to_datetime(
        weighted_avg_dataset["Year"].astype(str) + "-" + weighted_avg_dataset["Week"].astype(str) + "-1", format="%Y-%W-%w")
    weighted_avg_dataset = weighted_avg_dataset.sort_values(by="Year_Week")

    return weighted_avg_dataset

"""
# Example usage:
dataset = load_dataset("../Satellite_NDVI_data_construction.csv")
dataset = threshold_ndvi_data(dataset, lower_ndvi_threshold=0.3, upper_ndvi_threshold=0.55)
dataset = compute_ndvi_statistics(dataset)
dataset = resample_and_average_weekly(dataset)
weighted_avg_dataset = compute_weighted_average(dataset)
"""