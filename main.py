import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from Utils.load_dataset import load_dataset
from Utils.threshold_dataset import threshold_ndvi_data
from Utils.compute_statistics import compute_ndvi_statistics
from Utils.mean_weekly_resampling import resample_and_average_weekly

from page_low_kvds import page_low_or_no_kvds
from page_onset_kvds import page_onset_kvds
from page_enstablished_kvds import page_established_kvds


# Page Configuration
st.set_page_config(
    page_title="Zespri NDVI Plot - Lazio",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Sidebar for user input
def sidebar():
    with st.sidebar:
        st.title("NDVI Analysis Settings")

        # NDVI Threshold Selection (Numeric Input)
        upper_ndvi_threshold = st.number_input("Upper NDVI Threshold", min_value=0.0, max_value=1.0, value=0.55,
                                               step=0.01)
        lower_ndvi_threshold = st.number_input("Lower NDVI Threshold", min_value=0.0, max_value=1.0, value=0.3,
                                               step=0.01)
        if upper_ndvi_threshold < lower_ndvi_threshold:
            st.warning("Upper NDVI Threshold must be greater than or equal to the Lower NDVI Threshold.")
            raise ValueError(
                "Upper NDVI Threshold must be greater than or equal to the Lower NDVI Threshold.")

        # Visualization Type Selection (Dropdown Menu)
        visualization_options = ["Low or No KVDS", "Onset KVDS", "Established KVDS"]
        selected_visualization = st.selectbox("Select Visualization Type", visualization_options)

    return lower_ndvi_threshold, upper_ndvi_threshold, selected_visualization


# Determine which page to load
def main():

    # Load the dataset
    dataset_df = load_dataset("./Satellite_NDVI_data_construction_2.csv")

    # Sidebar for input parameters
    lower_ndvi_threshold, upper_ndvi_threshold, selected_visualization = sidebar()

    ########## Data Preprocessing ##########
    # Apply NDVI thresholding
    dataset = threshold_ndvi_data(dataset_df, lower_ndvi_threshold, upper_ndvi_threshold)
    # Compute NDVI statistics
    dataset = compute_ndvi_statistics(dataset)
    # Resample weekly for visualization
    dataset = resample_and_average_weekly(dataset)

    ########## Page Navigation ##########
    if selected_visualization == "Low or No KVDS":
        page_low_or_no_kvds(dataset)
    elif selected_visualization == "Onset KVDS":
        page_onset_kvds(dataset)
    elif selected_visualization == "Established KVDS":
        page_established_kvds(dataset)


if __name__ == "__main__":
    main()
