import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from select_kpin_block import select_kpin_and_block
from Utils.mean_weekly_resampling import resample_to_predefined_weeks

visualization_description = "Comparison of the average NDVI values of medium-NDVI pixels " \
    "in the selected field across different seasons."


def page_onset_kvds(dataset):
    st.title("Onset KVDS")
    st.markdown(f"**Description:** {visualization_description}")

    # KPIN and Block selection
    selected_kpin, selected_block, selected_primary_key = select_kpin_and_block(dataset)

    # Filter dataset by selected KPIN and Block
    selected_dataset = dataset[dataset["Primary_Key"] == selected_primary_key]
    if selected_dataset.empty:
        st.warning("No data available for the selected KPIN and Block.")
        return

    # Seasons selection
    season_options = selected_dataset["Year"].unique()
    season_options = season_options[season_options != 2025]  # TEMPORANEOUS FIX: Exclude 2025 data
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

    r1 = [x + 14 for x in range(len(selected_dataset["Week"].unique()))]

    plt.tight_layout()
    for i, season in enumerate(seasons):
        season_data = selected_dataset[selected_dataset["Year"] == season]
        if season_data.empty:
            st.warning(f"No data available for the selected season: {season}")
            continue

        ax1[0].plot(season_data["Week"], season_data["Mean_Yellow_Pixels"], marker='o', markersize=5,
                    label=f"Season: {season}")

    ax1[0].set_xlabel("Date")
    ax1[0].set_ylabel("Mean NDVI Pixels")
    ax1[0].set_title(f"Mean Green Pixels for Selected KPIN: {selected_kpin}, Block: {selected_block}")
    ax1[0].set_xticks(r1)
    ax1[0].set_xlim(13, 45)
    ax1[0].set_xticklabels(season_data['Year_Week'].dt.strftime('%m-%d'), rotation=90)
    ax1[0].legend()
    ax1[0].grid(True)

    # Plot the Number of Pixels for each season
    bar_width = 0.35
    for i, season in enumerate(seasons):
        season_data = selected_dataset[selected_dataset["Year"] == season]
        if season_data.empty:
            st.warning(f"No data available for the selected season: {season}")
            continue
        # Create discrete stacked plot in the superior subplot

        r1 = [x + 14 for x in range(len(season_data['Week']))]
        ax1[i + 1].bar(r1, season_data['Green_NDVI_Pixels_Number'], color='#006400',
                       width=bar_width, label='Green NDVI Pixels', align='center')
        ax1[i + 1].bar(r1, season_data['Yellow_NDVI_Pixels_Number'],
                       bottom=season_data['Green_NDVI_Pixels_Number'], color='#FFFF00',
                       width=bar_width, label='Yellow NDVI Pixels', align='center')
        ax1[i + 1].bar(r1, season_data['Red_NDVI_Pixels_Number'], color='#8B0000',
                       bottom=season_data['Green_NDVI_Pixels_Number'] + season_data['Yellow_NDVI_Pixels_Number'],
                       width=bar_width, label='Red NDVI Pixels', align='center')
        ax1[i + 1].set_xlabel('Date')
        ax1[i + 1].set_ylabel('Number of Pixels')
        ax1[i + 1].set_title(f'Distribution of NDVI Pixels, Season: {season}')
        ax1[i + 1].legend(loc='lower right')
        ax1[i + 1].grid(True)
        ax1[i + 1].set_xticks(r1)
        ax1[i + 1].set_xlim(13, 45)
        ax1[i + 1].set_xticklabels(season_data['Year_Week'].dt.strftime('%m-%d'), rotation=90)

    plt.suptitle(f'Distribution of NDVI Pixels')
    plt.tight_layout()

    st.pyplot(fig)
