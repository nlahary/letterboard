import pandas as pd
import streamlit as st


@st.cache
def compute_top10_by_filter(df: pd.DataFrame, filter_by: str, explode: bool = False) -> pd.DataFrame:
    """Compute top 10 countries, languages, or genres by count."""
    if explode:
        df = df[filter_by].explode()
    return df[filter_by].value_counts().head(10)
