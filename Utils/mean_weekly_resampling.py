import pandas as pd
import numpy as np
from Utils.load_dataset import load_dataset
from Utils.threshold_dataset import threshold_ndvi_data
from Utils.compute_statistics import compute_ndvi_statistics


def resample_and_average_weekly(dataset):
    # Group by Primary_Key, Year, and Week, then apply weighted averaging
    weekly_means = dataset.groupby(["Primary_Key", "Year", "Week"]).agg({
        # Non-aggregated features
        "KPIN": lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan,
        "Block_Name": lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan,
        "Orchard_Name": lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan,
        "Country_Name": lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan,
        "Supply_Area_Name": lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan,
        "Month": lambda x: x.min() if not x.empty else np.nan,
        "Day": lambda x: x.min() if not x.empty else np.nan,
        "Acquisition_Date": lambda x: x.min() if not x.empty else np.nan,
        "Total_Hectares": lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan,
        "Variety_Name": lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan,
        # Aggregated features with weighted mean calculations
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
        ),
        "Green_NDVI_Pixels_Number": 'mean',
        "Yellow_NDVI_Pixels_Number": 'mean',
        "Red_NDVI_Pixels_Number": 'mean',
        "Cloud_Or_Shadow_Percentage": 'mean',
        "Cloud_Or_Shadow_Return_Code": 'mean',

    }).reset_index()

    weekly_means["Year_Week"] = pd.to_datetime(
        weekly_means["Year"].astype(str) + "-" + weekly_means["Week"].astype(str) + "-1", format="%Y-%W-%w")
    weekly_means = weekly_means.sort_values(by="Year_Week")

    weekly_means = resample_to_predefined_weeks(weekly_means)
    #print(resample_to_predefined_weeks(weekly_means))
    #st.dataframe(resample_to_predefined_weeks(weekly_means))

    return weekly_means


def resample_to_predefined_weeks(dataset):
    # Define the predefined range of weeks (April to October)
    predefined_start_week = 14  # First week of April
    predefined_end_week = 44   # Last week of October

    # Create a complete range of weeks for each Primary_Key and Year
    complete_weeks = []
    for (primary_key, year), group in dataset.groupby(["Primary_Key", "Year"]):
        start_date = pd.to_datetime(f"{year}-{predefined_start_week}-1", format="%Y-%W-%w")
        end_date = pd.to_datetime(f"{year}-{predefined_end_week}-1", format="%Y-%W-%w")
        # Create weekly date range
        all_weeks = pd.date_range(start=start_date, end=end_date, freq="W-MON")
        # Append the DataFrame
        complete_weeks.append(pd.DataFrame({"Primary_Key": primary_key, "Year_Week": all_weeks}))

    # Concatenate all complete weeks
    complete_weeks_df = pd.concat(complete_weeks, ignore_index=True)

    """
    
    #complete_weeks_df["Week"] = complete_weeks_df["Year_Week"].dt.isocalendar().week
    #st.dataframe(complete_weeks_df)
    #st.dataframe(dataset)
    """

    # Merge the complete weeks with the original dataset
    resampled_dataset = pd.merge(complete_weeks_df, dataset, on=["Primary_Key", "Year_Week"], how="left")

    # Extract Year and Week from the resampled Year_Week
    resampled_dataset["Year"] = resampled_dataset["Year_Week"].dt.year
    resampled_dataset["Week"] = resampled_dataset["Year_Week"].dt.isocalendar().week
    resampled_dataset["KPIN"] = resampled_dataset["Primary_Key"].str.split("_").str[0].astype(int)
    resampled_dataset["Block_Name"] = resampled_dataset["Primary_Key"].str.split("_").str[1]

    return resampled_dataset


if __name__ == "__main__":
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
Primary_Key                          object
Year                                  int64
Week                                  int64
Mean_Green_Pixels                   float64
Mean_Yellow_Pixels                  float64
Mean_Red_Pixels                     float64
Green_NDVI_Pixels_Number            float64
Yellow_NDVI_Pixels_Number           float64
Red_NDVI_Pixels_Number              float64
Orchard_Name                         object
Country_Name                         object
Supply_Area_Name                     object
KPIN                                  int64
Block_Name                           object
Year_Week                    datetime64[ns]
dtype: object

Process finished with exit code 0
"""