import streamlit as st

def Navbar():
    with st.sidebar:
        st.page_link('standings_line.py', label='Standings and Streaks', icon='📈')
        st.page_link('pages/page2.py', label='Team Scoring', icon='⚾')