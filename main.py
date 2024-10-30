import asyncio
import httpx
import streamlit as st
from scrapper import get_total_pages, main
from visuals import *
from visuals_2 import *

from utils import compute_df_by_filter
import pandas as pd

st.set_page_config(layout="wide")  # Set the page layout to wide mode

st.title("Letterboard : Your Letterboxd Diary Analysis")

st.markdown(
    """
    Welcome to Letterboard! This app allows you to analyze your Letterboxd diary and discover interesting insights about your film-watching habits.
    Enter your Letterboxd username below and click the 'Fetch Diary' button to get started.

    Inspired by the work of Favour O. ([Link to GitHub](https://github.com/afoshiok/Letterboard))

    Made by [Nathanaël L.]
    """
)

# Session state variables
if 'username' not in st.session_state:
    st.session_state.username = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'selected_column' not in st.session_state:
    st.session_state.selected_column = "Country"
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Level.1"

username = st.text_input("Enter your Letterboxd username:",
                         value=st.session_state.username or "").strip()

if username and username != st.session_state.username:
    st.session_state.username = username

if st.button("Fetch Diary") and st.session_state.username:
    try:
        total_pages = get_total_pages(st.session_state.username)
    except httpx.HTTPStatusError:
        st.error(f"User '{
                 st.session_state.username}' not found. Please check the username and try again.")
    else:
        with st.spinner("Fetching data..."):
            try:
                df: pd.DataFrame = asyncio.run(
                    main(st.session_state.username, total_pages))
                st.session_state.df = df  # Save dataframe to session state
                st.success("Data fetched successfully!")
                if df.empty:
                    st.error(f"No data found for user '{
                             st.session_state.username}'. Please check the username and try again.")

            except AttributeError as e:
                if "PoolTimeoutError" in str(e):
                    st.error("The request timed out. Please try again.")
        if st.session_state.df.empty:
            st.error(f"No data found for user '{
                     st.session_state.username}'. Please check the username and try again.")

# Display data
if st.session_state.df is not None and not st.session_state.df.empty:
    tab_level1, tab_level2 = st.tabs(
        ["Page 1", "Page 2"])

    with tab_level1:
        # Two-by-two graph layout using columns
        col1, col2 = st.columns(2)

        with col1:
            fig = draw_top3(st.session_state.df)
            st.pyplot(fig)

        with col2:
            fig = draw_top_countries(st.session_state.df)
            st.plotly_chart(fig)

        col3, col4 = st.columns(2)

        with col3:
            fig = draw_log_timeline(st.session_state.df)
            st.plotly_chart(fig)

        with col4:
            fig = draw_top_genres(st.session_state.df)
            st.plotly_chart(fig)

        col5, col6 = st.columns(2)

        with col5:
            fig = draw_rating_dist(st.session_state.df)
            st.plotly_chart(fig)

        with col6:
            fig = draw_top_actors(st.session_state.df)
            st.plotly_chart(fig)

    with tab_level2:

        col1, col2 = st.columns([0.2, 0.2])

        with col1:
            fig, title, subtitle = draw_studios_radar(st.session_state.df)
            st.markdown(f"""
            # {title}
            {subtitle}
            """)
            st.pyplot(fig)

        with col2:
            fig, title, subtitle = draw_decades_radar(st.session_state.df)
            st.markdown(f"""
            # {title}
            {subtitle}
            """)
            st.pyplot(fig)

        cont = st.container(border=True)
        with cont:
            fig, title, subtitle = draw_lang_sankey(st.session_state.df)
            st.markdown(f"""
                    # {title}
                    {subtitle}
                    """)
            st.plotly_chart(fig)

        st.session_state.selected_column = selected_column
        df_filtered = compute_df_by_filter(
            st.session_state.df, st.session_state.selected_column)
        st.write(df_filtered)
