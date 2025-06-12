import streamlit as st

def page_established_kvds(dataset):
    st.title("Established KVDS")
    st.markdown(f"**Description:** To be added later.")

    # KPIN and Block selection
    col1, col2 = st.columns(2)
    with col1:
        kpin_options = sorted(dataset["KPIN"].unique())
        selected_kpin = st.selectbox("Select KPIN", kpin_options)
    with col2:
        filtered_blocks = dataset[dataset["KPIN"] == selected_kpin]["Block_Name"].unique()
        selected_block = st.selectbox("Select Block", filtered_blocks)

    # Plot