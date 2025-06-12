import streamlit as st

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
        orchard_options = dataset["Orchard_Name"].dropna().unique()
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
