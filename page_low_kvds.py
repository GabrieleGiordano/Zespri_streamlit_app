import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from Utils.mean_weekly_resampling import resample_and_average_weekly
from Utils.compute_area_aggregation import compute_weighted_average
from select_kpin_block import select_kpin_and_block


visualization_description = "Comparison of the average NDVI values of high-NDVI pixels in the selected field versus those "\
                      "in the selected comparison group (region or area)."


def page_low_or_no_kvds(dataset):
    st.title("Low or No KVDS")
    st.markdown(f"**Description:** {visualization_description}")

    # KPIN and Block selection
    selected_kpin, selected_block, selected_primary_key = select_kpin_and_block(dataset)

    # Area selection
    area_options = dataset["Supply_Area_Name"].dropna().unique()
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

    # resample the datasets to weekly averages
    area_aggregation_dataset = resample_and_average_weekly(area_aggregation_dataset)

    # display the selected dataset
    st.dataframe(selected_dataset)
    st.dataframe(area_aggregation_dataset)

    # Placeholder for NDVI trend comparison plot
    st.subheader("NDVI Trend Comparison")
    st.write("Compare NDVI trends of the selected field vs the selected area (not including the selected filed)")

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 10), gridspec_kw={'height_ratios': [2, 1, 1]})

    r1 = [x + 14 for x in range(selected_dataset.shape[0])]

    # Plot the Mean NDVI of Green Pixels for the selected KPIN and Block and for the selected area
    ax1.plot(selected_dataset["Week"], selected_dataset["Mean_Green_Pixels"], color='green', marker='o',
             markersize=5,
             label=f"KPIN: {selected_kpin}, Block: {selected_block} - Mean Green Pixels")
    ax1.plot(area_aggregation_dataset["Week"], area_aggregation_dataset["Mean_Green_Pixels"], color='lightgreen',
             marker='o', markersize=5,
             linestyle='--', label=f"Area: {selected_area}")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Mean NDVI Pixels")
    ax1.set_title(f"Mean Green Pixels for KPIN: {selected_kpin}, Block: {selected_block}, Season: {selected_season}")
    ax1.legend()
    ax1.grid(True)
    ax1.set_xticks(r1)
    ax1.set_xlim(13, 45)
    ax1.set_xticklabels(selected_dataset["Year_Week"].dt.strftime('%m-%d'), rotation=90)

    # Plot the Number of Green NDVI Pixels for the selected KPIN and Block and for the selected area
    # Create discrete stacked plot in the superior subplot
    bar_width = 0.35
    ax2.bar(r1, selected_dataset['Green_NDVI_Pixels_Number'], color='#006400',
            width=bar_width, label='Green NDVI Pixels')  # Darker green
    ax2.bar(r1, selected_dataset['Yellow_NDVI_Pixels_Number'],
            bottom=selected_dataset['Green_NDVI_Pixels_Number'], color='#FFFF00',
            width=bar_width, label='Yellow NDVI Pixels')  # Lighter yellow
    ax2.bar(r1, selected_dataset['Red_NDVI_Pixels_Number'],
            bottom=selected_dataset['Green_NDVI_Pixels_Number'] +
                   selected_dataset['Yellow_NDVI_Pixels_Number'], color='#8B0000',
            width=bar_width, label='Red NDVI Pixels')  # Darker red

    ax2.set_xlabel('Date')
    ax2.set_ylabel('Number of Pixels')
    ax2.set_title(f'Distribution of NDVI Pixels, KPIN:{selected_kpin}, Block:{selected_block}, Season: {selected_season}')
    ax2.legend(loc='lower right')
    ax2.grid(True)
    ax2.set_xticks(r1)
    ax2.set_xlim(13, 45)
    ax2.set_xticklabels(selected_dataset['Year_Week'].dt.strftime('%m-%d'), rotation=90)

    # Create discrete stacked plot in the inferior subplot
    ax3.bar(r1, area_aggregation_dataset['Green_NDVI_Pixels_Number'], color='#006400',
            width=bar_width, label='Green NDVI Pixels')  # Darker green
    ax3.bar(r1, area_aggregation_dataset['Yellow_NDVI_Pixels_Number'],
            bottom=area_aggregation_dataset['Green_NDVI_Pixels_Number'], color='#FFFF00',
            width=bar_width, label='Yellow NDVI Pixels')  # Lighter yellow
    ax3.bar(r1, area_aggregation_dataset['Red_NDVI_Pixels_Number'],
            bottom=area_aggregation_dataset['Green_NDVI_Pixels_Number'] + area_aggregation_dataset[
                'Yellow_NDVI_Pixels_Number'],
            color='#8B0000', width=bar_width, label='Red NDVI Pixels')  # Darker red
    ax3.set_xlabel('Date')
    ax3.set_ylabel('Number of Pixels')
    ax3.set_title(f'Distribution of NDVI Pixels, {selected_area} area, Season: {selected_season}')
    ax3.grid(True)
    ax3.set_xticks(r1)
    ax3.set_xlim(13, 45)
    ax3.set_xticklabels(area_aggregation_dataset['Year_Week'].dt.strftime('%m-%d'), rotation=90)

    plt.tight_layout()
    st.pyplot(fig)