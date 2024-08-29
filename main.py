import asyncio
import httpx
import streamlit as st
from scrapper import get_total_pages, main
from visuals_2 import *
from visuals import *
from logger import logger

st.title("Letterboard : Your Letterboxd Diary Analysis")

st.markdown(
    """
    Welcome to Letterboard! This app allows you to analyze your Letterboxd diary and discover interesting insights about your film-watching habits.
    Enter your Letterboxd username below and click the 'Fetch Diary' button to get started.

    Inspired by the work of Favour O. ([Link to GitHub](https://github.com/afoshiok/Letterboard))

    Made by [Nathanaël L.]
    """
)

# Initialize session state variables
if 'username' not in st.session_state:
    st.session_state.username = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'selected_column' not in st.session_state:
    st.session_state.selected_column = "Country"
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Level.1"

logger.info(f"Script started with session state: {
            st.session_state.username}, & {st.session_state.selected_column}")
logger.info("*"*50)
# Input for the username
username = st.text_input("Enter your Letterboxd username:",
                         value=st.session_state.username or "").strip()
logger.info(f"Username: {username}")

# Update session state with the username input
if username and username != st.session_state.username:
    logger.info(f"Username updated: {username}")
    st.session_state.username = username
    logger.info(f" Session state username: {st.session_state.username}")

# """ fetch data"""
if st.button("Fetch Diary") and st.session_state.username:
    logger.info(f"Fetching data for user: {st.session_state.username}")
    try:
        total_pages = get_total_pages(st.session_state.username)
    except httpx.HTTPStatusError:
        st.error(f"User '{
                 st.session_state.username}' not found. Please check the username and try again.")
    else:
        with st.spinner("Fetching data..."):
            try:
                df = asyncio.run(
                    main(st.session_state.username, total_pages))
                st.session_state.df = df  # Save dataframe to session state
                logger.info(f"Dataframe: {df.head()}")
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


# Create tabs for different levels


# """ display data """
if st.session_state.df is not None and not st.session_state.df.empty:
    tab_level1, tab_level2, tab_level3 = st.tabs(
        ["Level 1", "Level 2", "Level 3"])

    with tab_level1:

        fig = draw_top3(st.session_state.df)
        st.pyplot(fig)

        fig = draw_top_countries(st.session_state.df)
        st.plotly_chart(fig)

        fig = draw_log_timeline(st.session_state.df)
        st.plotly_chart(fig)

        fig = draw_top_genres(st.session_state.df)
        st.plotly_chart(fig)

        fig = draw_rating_dist(st.session_state.df)
        st.plotly_chart(fig)

        fig = draw_top_actors(st.session_state.df)
        st.plotly_chart(fig)

    with tab_level2:
        fig, title, subtitle = draw_studios_radar(st.session_state.df)
        st.markdown(f"""
        # {title}
        {subtitle}
        """)
        st.pyplot(fig)

        fig, title, subtitle = draw_decades_radar(st.session_state.df)
        st.markdown(f"""
        # {title}
        {subtitle}
        """)
        st.pyplot(fig)

        fig, title, subtitle = draw_lang_sankey(st.session_state.df)
        st.markdown(f"""
        # {title}
        {subtitle}
        """)
        st.plotly_chart(fig)

    with tab_level3:
        if st.session_state.df is not None:
            selected_column = st.selectbox(
                "Filter by:",
                ["Country", "Language", "Genre"],
                index=0 if st.session_state.selected_column is None else [
                    "Country", "Language", "Genre"].index(st.session_state.selected_column)
            )

            st.session_state.selected_column = selected_column
            logger.info(f"Selected column: {
                st.session_state.selected_column}")

        # if st.session_state.selected_column:
        #     st.session_state.filter_by = st.session_state.selected_column
            if st.session_state.selected_column == "Country":
                logger.info(f'Country chosen : session state {
                    st.session_state.selected_column}')
                # Show top countries and their counts
                df_country = st.session_state.df["country"].value_counts(
                ).reset_index()
                df_country.columns = ["Country", "Count"]
                st.write(df_country)

            elif st.session_state.selected_column == "Language":
                logger.info(f'Country chosen : session state {
                    st.session_state.selected_column}')

                # Show top languages and their counts
                df_lang = st.session_state.df["primary_language"].value_counts(
                ).reset_index()
                df_lang.columns = ["Language", "Count"]
                st.write(df_lang)

            elif st.session_state.selected_column == "Genre":
                logger.info(f'Country chosen : session state {
                    st.session_state.selected_column}')

                # Show top genres and their counts
                df_genre = st.session_state.df["genres"].explode(
                ).value_counts().reset_index()
                df_genre.columns = ["Genre", "Count"]
                st.write(df_genre)

#  Display the state variables for debugging
st.write(st.session_state.selected_column)
logger.info(f"end of script with session state: {
            st.session_state.username}, & {st.session_state.selected_column} \n")
