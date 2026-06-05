import streamlit as st

def Navbar():
    with st.sidebar:
        st.page_link('standings_line.py', label='Standings and Streaks', icon='📈')
        st.page_link('pages/team_stats.py', label='Team Scoring', icon='⚾')
        st.page_link('pages/player_stats.py', label='Player Scoring', icon='⚾')