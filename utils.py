import pandas as pd
import streamlit as st


@st.cache_data
def compute_df_by_filter(df: pd.DataFrame, filter_column: str) -> pd.DataFrame:

    filter = filter_column.lower().replace(" ", "_")

    if filter_column in ["Country", "Language"]:
        df_filtered = df[filter].value_counts().reset_index()
        df_filtered.columns = [filter_column, "Count"]
        return df_filtered
    else:
        df_filtered = df[filter].explode().value_counts().reset_index()
        df_filtered.columns = [filter_column, "Count"]
        return df_filtered
