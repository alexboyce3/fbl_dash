import streamlit as st
import pandas as pd
from utils import stat_summary, plot_points, style_pts
from streamlit_utils import Navbar

st.set_page_config(page_title="Team Scoring", layout="centered")

def main():
    Navbar()

    st.title(f'⚾ Team Scoring')

if __name__ == '__main__':
    main()


tab1, tab2 = st.tabs(["Points Rankings", "Stats Rankings"])
df = pd.read_csv("data/team_week_points.csv")
SEASON = 2026
WEEK = df[df['season'] == SEASON]['week'].max()
WEEK_TYPE = df[(df['season'] == SEASON) & (df['week'] == WEEK)]['week_type'].iloc[0]

with tab1:
    st.title("Latest Week Points Rankings")

    tmp = df[df['week_type'] == WEEK_TYPE].copy()

    pts_select = st.selectbox("Select points", ['total', 'hitting', 'pitching'], key='tab1')

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
    st.dataframe(hit_table, use_container_width=False)
    
    pitch = pd.read_csv("data/pitching_stats.csv")
    pitch_table = stat_summary(pitch, SEASON, WEEK)
    st.header("This Week's Pitching Stats")
    st.dataframe(pitch_table, use_container_width=False)


with tab2:
    st.title("Season to date points")

    pts_select = st.selectbox("Select points", ['total', 'hitting', 'pitching'], key='tab2')

    if pts_select == 'total':
        pts_col = 'team_points'
        label = 'Team Points'
    elif pts_select == 'hitting':
        pts_col = 'hitting_points'
        label = 'Hitting Points'
    else:
        pts_col = 'pitching_points'
        label = 'Pitching Points'

    tmp = df.copy()
    tmp['points_week_rank'] = tmp.groupby(['season', 'week'])[pts_col].rank(ascending=False, method='min')
    current_season = tmp[tmp['season'] == SEASON].copy()
    cols_to_color = list(current_season[current_season['week_type'] == 'normal']['week'].unique())
    weekly_points = pd.pivot_table(current_season, index=['manager'], columns=['week'], values=pts_col).reset_index()
    pts_table = style_pts(weekly_points, False, cols_to_color)

    weekly_points = pd.pivot_table(current_season,
                                    index=['manager'],
                                    columns=['week'],
                                    values='points_week_rank').reset_index()
    for col in weekly_points.columns:
        if col != 'manager':
            weekly_points[col] = weekly_points[col].astype(int)

    rank_table = style_pts(weekly_points, True)
    st.header(f"Season {label}")
    st.dataframe(pts_table, use_container_width=False)

    st.header(f"Season {label} Rank")
    st.dataframe(rank_table, use_container_width=False)