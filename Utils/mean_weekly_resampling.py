import pandas as pd
import numpy as np
from Utils.load_dataset import load_dataset
from Utils.threshold_dataset import threshold_ndvi_data
from Utils.compute_statistics import compute_ndvi_statistics


def resample_and_average_weekly(dataset):
    # Group by Primary_Key, Year, and Week, then apply weighted averaging
    weekly_means = dataset.groupby(["Primary_Key", "Year", "Week"]).apply(
        lambda group: pd.Series({
            "Mean_Green_Pixels": (
                (group["Mean_Green_Pixels"] * group["Green_NDVI_Pixels_Number"]).sum() /
                group["Green_NDVI_Pixels_Number"].sum()
                if group["Green_NDVI_Pixels_Number"].sum() > 0 else np.nan
            ),
            "Mean_Yellow_Pixels": (
                (group["Mean_Yellow_Pixels"] * group["Yellow_NDVI_Pixels_Number"]).sum() /
                group["Yellow_NDVI_Pixels_Number"].sum()
                if group["Yellow_NDVI_Pixels_Number"].sum() > 0 else np.nan
            ),
            "Mean_Red_Pixels": (
                (group["Mean_Red_Pixels"] * group["Red_NDVI_Pixels_Number"]).sum() /
                group["Red_NDVI_Pixels_Number"].sum()
                if group["Red_NDVI_Pixels_Number"].sum() > 0 else np.nan
            ),
            "Green_NDVI_Pixels_Number": group["Green_NDVI_Pixels_Number"].sum() / len(group),
            "Yellow_NDVI_Pixels_Number": group["Yellow_NDVI_Pixels_Number"].sum() / len(group),
            "Red_NDVI_Pixels_Number": group["Red_NDVI_Pixels_Number"].sum() / len(group),
        })
    ).reset_index()

    # Extract unique Primary_Key mappings for Orchard_Name, Country_Name, and Supply_Area_Name
    primary_key_mapping = dataset[["Primary_Key", "Orchard_Name", "Country_Name", "Supply_Area_Name"]].drop_duplicates()

    # Merge the resampled data with the mapping to include the additional columns
    weekly_means = weekly_means.merge(primary_key_mapping, on="Primary_Key", how="left")

    weekly_means["KPIN"] = weekly_means["Primary_Key"].apply(lambda x: x.split("_")[0])
    weekly_means["Block_Name"] = weekly_means["Primary_Key"].apply(lambda x: x.split("_")[1])

    weekly_means["Year_Week"] = pd.to_datetime(
        weekly_means["Year"].astype(str) + "-" + weekly_means["Week"].astype(str) + "-1", format="%Y-%W-%w")
    weekly_means = weekly_means.sort_values(by="Year_Week")

    #weekly_means = resample_to_predefined_weeks(weekly_means)

    return weekly_means

"""
# Example usage:
dataset = load_dataset("../Satellite_NDVI_data_construction.csv")
dataset = threshold_ndvi_data(dataset, lower_ndvi_threshold=0.3, upper_ndvi_threshold=0.55)
dataset = compute_ndvi_statistics(dataset)
print(dataset.columns)  # Check the new columns added
print(dataset.dtypes)

weekly_resampled_data = resample_and_average_weekly(dataset)
print(weekly_resampled_data.head())
print(weekly_resampled_data.dtypes)  # Check the new columns added
"""


def resample_to_predefined_weeks(dataset):
    # Define the predefined range of weeks (April to October)
    predefined_start_week = 14  # First week of April
    predefined_end_week = 43   # Last week of October

    # Create a complete range of weeks for each Primary_Key and Year
    complete_weeks = []
    for (primary_key, year), group in dataset.groupby(["Primary_Key", "Year"]):
        all_weeks = pd.date_range(
            start=f"{year}-W{predefined_start_week}-1",
            end=f"{year}-W{predefined_end_week}-1",
            freq="W-MON"
        )
        complete_weeks.append(pd.DataFrame({"Primary_Key": primary_key, "Year_Week": all_weeks}))

    # Concatenate all complete weeks
    complete_weeks_df = pd.concat(complete_weeks, ignore_index=True)

    # Merge the complete weeks with the original dataset
    dataset["Year_Week"] = pd.to_datetime(
        dataset["Year"].astype(str) + "-W" + dataset["Week"].astype(str) + "-1", format="%Y-%W-%w"
    )
    resampled_dataset = pd.merge(complete_weeks_df, dataset, on=["Primary_Key", "Year_Week"], how="left")

    # Extract Year and Week from the resampled Year_Week
    resampled_dataset["Year"] = resampled_dataset["Year_Week"].dt.year
    resampled_dataset["Week"] = resampled_dataset["Year_Week"].dt.isocalendar().week

    return resampled_dataset

"""
# Example usage:
resampled_data = resample_to_predefined_weeks(weekly_resampled_data)
print(resampled_data.head())
"""