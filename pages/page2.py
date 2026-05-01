import streamlit as st
import pandas as pd
from utils import stat_summary, plot_points

tab1, tab2 = st.tabs(["Points Rankings", "Stats Rankings"])


with tab1:
    st.title("Latest Week Points Rankings")

    df = pd.read_csv("data/team_week_points.csv")
    SEASON = 2026
    WEEK = df[df['season'] == SEASON]['week'].max()
    WEEK_TYPE = df[(df['season'] == SEASON) & (df['week'] == WEEK)]['week_type'].iloc[0]
    tmp = df[df['week_type'] == WEEK_TYPE].copy()

    pts_select = st.selectbox("Select points", ['total', 'hitting', 'pitching'])

    if pts_select == 'total':
        pts_col = 'team_points'
        label = 'Team Points'
    elif pts_select == 'hitting':
        pts_col = 'hitting_points'
        label = 'Hitting Points'
    else:
        pts_col = 'pitching_points'
        label = 'Pitching Points'
    plot = plot_points(tmp, pts_col, label, SEASON, WEEK)
    st.plotly_chart(plot, use_container_width=True)

    

    hit = pd.read_csv("data/hitting_stats.csv")
    hit_table = stat_summary(hit, SEASON, WEEK)
    st.header("This Week's Hitting Stats")
    st.dataframe(hit_table, use_container_width=False, hide_index=True)
    
    pitch = pd.read_csv("data/pitching_stats.csv")
    pitch_table = stat_summary(pitch, SEASON, WEEK)
    st.header("This Week's Pitching Stats")
    st.dataframe(pitch_table, use_container_width=False, hide_index=True)


with tab2:
    st.title("Latest Week Stats Rankings")
