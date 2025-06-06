import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from Utils.load_dataset import load_dataset
from Utils.threshold_dataset import threshold_ndvi_data
from Utils.compute_statistics import compute_ndvi_statistics
from Utils.mean_weekly_resampling import resample_and_average_weekly
from Utils.compute_area_aggregation import compute_weighted_average

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
        lower_ndvi_threshold = st.number_input("Lower NDVI Threshold", min_value=0.0, max_value=1.0, value=0.3,
                                               step=0.01)
        upper_ndvi_threshold = st.number_input("Upper NDVI Threshold", min_value=0.0, max_value=1.0, value=0.55,
                                               step=0.01)

        # Visualization Type Selection (Dropdown Menu)
        visualization_options = ["Low or No KVDS", "Onset KVDS", "Established KVDS"]
        selected_visualization = st.selectbox("Select Visualization Type", visualization_options)

    return lower_ndvi_threshold, upper_ndvi_threshold, selected_visualization

def select_kpin_and_block(dataset):
    """
    Creates a Streamlit UI for selecting a KPIN and Block from the dataset.

    Args:
        dataset (pd.DataFrame): The dataset containing 'Orchard_Name', 'KPIN', and 'Block_Name' columns.

    Returns:
        tuple: A tuple containing the selected KPIN, Block, and Primary Key.
    """
    col1, col2 = st.columns(2)
    with col1:
        orchard_options = dataset["Orchard_Name"].unique()
        if len(orchard_options) == 0:
            st.warning("No orchards available in the dataset.")
            return None, None, None
        selected_orchard = st.selectbox("Select Orchard", sorted(orchard_options))
        selected_kpin = int(selected_orchard.replace("_", " ").split("-")[0])
    with col2:
        filtered_blocks = dataset[dataset["KPIN"] == selected_kpin]["Block_Name"].unique()
        selected_block = st.selectbox("Select Block",
                                      filtered_blocks if len(filtered_blocks) > 0 else ["No Blocks Available"])
    selected_primary_key = f"{selected_kpin}_{selected_block}"
    return selected_kpin, selected_block, selected_primary_key


# Descriptions for each visualization type
visualization_descriptions = {
    "Low or No KVDS": "Comparison of the average NDVI values of high-NDVI pixels in the selected field versus those "
                      "in the selected comparison group (region or area).",
    "Onset KVDS": "Comparison of the average NDVI values of medium-NDVI pixels in the selected field across different "
                  "seasons.",
    "Established KVDS": "TO BE ADDED"
}

# Temporary empty DataFrame for demonstration purposes
dataset_df = load_dataset("./Satellite_NDVI_data_construction_2.csv")


# Define visualization page functions
def page_low_or_no_kvds(dataset):
    st.title("Low or No KVDS")
    st.markdown(f"**Description:** {visualization_descriptions['Low or No KVDS']}")

    # KPIN and Block selection
    selected_kpin, selected_block, selected_primary_key = select_kpin_and_block(dataset)

    # Area selection
    area_options = dataset["Supply_Area_Name"].unique()
    selected_area_default = dataset[(dataset["KPIN"] == selected_kpin) & (dataset["Block_Name"] == selected_block)][
            "Supply_Area_Name"].iloc[0]
    selected_area = st.selectbox("Select Area", area_options if len(area_options) > 0 else ["No Areas Available"],
                                 index=area_options.tolist().index(
                                     selected_area_default) if selected_area_default in area_options else 0)

    # Season selection
    season_options = dataset["Year"].unique()
    selected_season = st.selectbox("Select Season",
                                   season_options if len(season_options) > 0 else ["No Seasons Available"])

    # Extract data for the selected KPIN and Block and for the selected area (except for selected KPIN and Block)
    selected_dataset = dataset[(dataset["KPIN"] == selected_kpin) & (dataset["Block_Name"] == selected_block)
                               & (dataset["Year"] == selected_season)]
    comparison_dataset = dataset[
        (dataset["Supply_Area_Name"] == selected_area) & (dataset["Primary_Key"] != selected_primary_key) &
        (dataset["Year"] == selected_season)]
    if selected_dataset.empty:
        st.warning("No data available for the selected KPIN and Block.")
        # return
    if comparison_dataset.empty:
        st.warning("No comparison data available for the selected area.")
        # return

    # Compute the aggregation for the selected area
    area_aggregation_dataset = compute_weighted_average(comparison_dataset)

    # display the selected dataset
    st.dataframe(selected_dataset)
    st.dataframe(comparison_dataset)

    # Placeholder for NDVI trend comparison plot
    st.subheader("NDVI Trend Comparison")
    st.write("Compare NDVI trends of the selected field vs the selected area (not including the selected filed)")

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 10), gridspec_kw={'height_ratios': [2, 1, 1]})
    plt.tight_layout()

    # Plot the Mean NDVI of Green Pixels for the selected KPIN and Block and for the selected area
    ax1.plot(selected_dataset["Year_Week"], selected_dataset["Mean_Green_Pixels"], color='green', marker='o',
             markersize=5,
             label=f"KPIN: {selected_kpin}, Block: {selected_block} - Mean Green Pixels")
    ax1.plot(area_aggregation_dataset["Year_Week"], area_aggregation_dataset["Mean_Green_Pixels"], color='lightgreen',
             marker='o', markersize=5,
             linestyle='--', label=f"Area: {selected_area}")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Mean NDVI Pixels")
    ax1.set_title("Mean Green Pixels")
    ax1.legend()
    ax1.grid(True)
    plt.xticks(rotation=45)

    # Plot the Number of Green NDVI Pixels for the selected KPIN and Block and for the selected area
    # Create discrete stacked plot in the superior subplot
    bar_width = 0.35
    r1 = range(len(selected_dataset['Year_Week']))
    ax2.bar(r1, selected_dataset['Green_NDVI_Pixels_Number'], color='#006400',
            width=bar_width, label='Green NDVI Pixels')  # Darker green
    ax2.bar(r1, selected_dataset['Yellow_NDVI_Pixels_Number'],
            bottom=selected_dataset['Green_NDVI_Pixels_Number'], color='#FFFF00',
            width=bar_width, label='Yellow NDVI Pixels')  # Lighter yellow
    ax2.bar(r1, selected_dataset['Red_NDVI_Pixels_Number'],
            bottom=selected_dataset['Green_NDVI_Pixels_Number'] +
                   selected_dataset['Yellow_NDVI_Pixels_Number'], color='#8B0000',
            width=bar_width, label='Red NDVI Pixels')  # Darker red

    plt.suptitle(f'Distribution of NDVI Pixels')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Number of Pixels')
    ax2.set_title(f'KPIN:{selected_kpin}, Block:{selected_block}')
    ax2.legend(loc='lower right')
    ax2.grid(True)
    ax2.set_xticks(r1)
    ax2.set_xticklabels(selected_dataset['Year_Week'].dt.strftime('%Y-%m-%d'), rotation=45)

    # Create discrete stacked plot in the inferior subplot
    r2 = range(len(area_aggregation_dataset['Year_Week']))
    ax3.bar(r2, area_aggregation_dataset['Green_NDVI_Pixels_Number'], color='#006400',
            width=bar_width, label='Green NDVI Pixels')  # Darker green
    ax3.bar(r2, area_aggregation_dataset['Yellow_NDVI_Pixels_Number'],
            bottom=area_aggregation_dataset['Green_NDVI_Pixels_Number'], color='#FFFF00',
            width=bar_width, label='Yellow NDVI Pixels')  # Lighter yellow
    ax3.bar(r2, area_aggregation_dataset['Red_NDVI_Pixels_Number'],
            bottom=area_aggregation_dataset['Green_NDVI_Pixels_Number'] + area_aggregation_dataset[
                'Yellow_NDVI_Pixels_Number'],
            color='#8B0000', width=bar_width, label='Red NDVI Pixels')  # Darker red
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Number of Pixels')
    ax3.set_title(f'{selected_area} area')
    ax3.grid(True)
    ax3.set_xticks(r2)
    ax3.set_xticklabels(area_aggregation_dataset['Year_Week'].dt.strftime('%Y-%m-%d'), rotation=45)

    plt.tight_layout()
    st.pyplot(fig)


def page_onset_kvds(dataset):
    st.title("Onset KVDS")
    st.markdown(f"**Description:** {visualization_descriptions['Onset KVDS']}")

    # KPIN and Block selection
    selected_kpin, selected_block, selected_primary_key = select_kpin_and_block(dataset)

    # Filter dataset by selected KPIN and Block
    selected_dataset = dataset[dataset["Primary_Key"] == selected_primary_key]
    if selected_dataset.empty:
        st.warning("No data available for the selected KPIN and Block.")
        return

    # Seasons selection
    season_options = selected_dataset["Year"].unique()
    seasons = st.multiselect("Select Seasons", season_options, default=season_options)

    # Filter dataset by selected seasons
    selected_dataset = selected_dataset[selected_dataset["Year"].isin(seasons)]

    # display the selected dataset
    st.dataframe(selected_dataset)

    # Placeholder for seasonal NDVI comparison plot
    st.subheader("Seasonal NDVI Analysis")
    st.write("Compare NDVI trends of the selected field across different seasons.")

    # to plot superimposed lines, we need to create a new column for the week of the year

    fig, ax1 = plt.subplots(len(seasons) + 1, 1, figsize=(7, 10),
                            gridspec_kw={'height_ratios': [2] + [1] * len(seasons)})
    plt.tight_layout()
    for i, season in enumerate(seasons):
        season_data = selected_dataset[selected_dataset["Year"] == season]
        if season_data.empty:
            st.warning(f"No data available for the selected season: {season}")
            continue
        # plot superimposed lines, use the same year (1900) as reference

        ax1[0].plot(season_data["Week"], season_data["Mean_Yellow_Pixels"], marker='o', markersize=5,
                    label=f"Season: {season}")

    ax1[0].set_xlabel("Date")
    ax1[0].set_ylabel("Mean NDVI Pixels")
    ax1[0].set_title(f"Mean Green Pixels for Selected KPIN: {selected_kpin}, Block: {selected_block}")
    ax1[0].legend()
    ax1[0].grid(True)
    plt.xticks(rotation=45)

    # Plot the Number of Pixels for each season
    bar_width = 0.35
    for i, season in enumerate(seasons):
        season_data = selected_dataset[selected_dataset["Year"] == season]
        if season_data.empty:
            st.warning(f"No data available for the selected season: {season}")
            continue
        # Create discrete stacked plot in the superior subplot
        r1 = range(len(season_data['Week']))
        ax1[i + 1].bar(r1, season_data['Green_NDVI_Pixels_Number'], color='#006400',
                       width=bar_width, label='Green NDVI Pixels')
        ax1[i + 1].bar(r1, season_data['Yellow_NDVI_Pixels_Number'],
                       bottom=season_data['Green_NDVI_Pixels_Number'], color='#FFFF00',
                       width=bar_width, label='Yellow NDVI Pixels')
        ax1[i + 1].bar(r1, season_data['Red_NDVI_Pixels_Number'], color='#8B0000',
                       bottom=season_data['Green_NDVI_Pixels_Number'] + season_data['Yellow_NDVI_Pixels_Number'],
                       width=bar_width, label='Red NDVI Pixels')
        ax1[i + 1].set_xlabel('Date')
        ax1[i + 1].set_ylabel('Number of Pixels')
        ax1[i + 1].set_title(f'Season: {season}')
        # ax1[i + 1].legend(loc='lower right')
        ax1[i + 1].grid(True)
        ax1[i + 1].set_xticks(r1)
        ax1[i + 1].set_xticklabels(season_data['Year_Week'].dt.strftime('%Y-%m-%d'), rotation=45)

    plt.suptitle(f'Distribution of NDVI Pixels')
    plt.tight_layout()

    st.pyplot(fig)


def page_established_kvds(dataset):
    st.title("Established KVDS")
    st.markdown(f"**Description:** {visualization_descriptions['Established KVDS']}")

    # KPIN and Block selection
    col1, col2 = st.columns(2)
    with col1:
        kpin_options = sorted(dataset["KPIN"].unique())
        selected_kpin = st.selectbox("Select KPIN", kpin_options)
    with col2:
        filtered_blocks = dataset[dataset["KPIN"] == selected_kpin]["Block_Name"].unique()
        selected_block = st.selectbox("Select Block", filtered_blocks)

    # Plot


# Determine which page to load
def main():
    # Sidebar for user input
    lower_ndvi_threshold, upper_ndvi_threshold, selected_visualization = sidebar()

    # Apply NDVI thresholding
    dataset = threshold_ndvi_data(dataset_df, lower_ndvi_threshold, upper_ndvi_threshold)
    # Compute NDVI statistics
    dataset = compute_ndvi_statistics(dataset)
    # Resample weekly for visualization
    dataset = resample_and_average_weekly(dataset)

    if selected_visualization == "Low or No KVDS":
        page_low_or_no_kvds(dataset)
    elif selected_visualization == "Onset KVDS":
        page_onset_kvds(dataset)
    elif selected_visualization == "Established KVDS":
        page_established_kvds(dataset)


if __name__ == "__main__":
    main()
