import streamlit as st


def dataset_block_for_prompt() -> str:
    df = st.session_state.get("uploaded_df")
    if df is None:
        return ""

    sample_csv = df.head(80).to_csv(index=False)
    return (
        "\n\nDATASET (CSV):\n"
        + sample_csv
        + "\n\nIf the question refers to the dataset, use ONLY this data.\n"
    )
