import streamlit as st
import pandas as pd
from utils import (
    stat_summary, 
    plot_points, 
    style_pts, 
    style_stat_summary
)
from streamlit_utils import Navbar
import plotly.graph_objects as go

st.set_page_config(page_title="Team Scoring", layout="centered")


@st.cache_data(show_spinner=False)
def load_team_week_points():
    return pd.read_csv("data/team_week_points.csv")

@st.cache_data(show_spinner=False)
def load_hitting_stats():
    return pd.read_csv("data/hitting_stats.csv")

@st.cache_data(show_spinner=False)
def load_pitching_stats():
    return pd.read_csv("data/pitching_stats.csv")

@st.cache_data(show_spinner=False)
def get_week_stat_summary(df, season, week):
    return stat_summary(df, season, week)

@st.cache_data(show_spinner=False)
def build_season_tables(df, season, pts_col):
    tmp = df.copy()
    tmp['points_week_rank'] = tmp.groupby(['season', 'week'])[pts_col].rank(ascending=False, method='min')
    current_season = tmp[tmp['season'] == season].copy()
    cols_to_color = list(current_season[current_season['week_type'] == 'normal']['week'].unique())

    weekly_points = pd.pivot_table(current_season, index=['manager'], columns=['week'], values=pts_col).reset_index()

    weekly_rank = pd.pivot_table(
        current_season,
        index=['manager'],
        columns=['week'],
        values='points_week_rank'
    ).reset_index()
    for col in weekly_rank.columns:
        if col != 'manager':
            weekly_rank[col] = weekly_rank[col].astype(int)
    return weekly_points, weekly_rank, cols_to_color

def style_season_tables(weekly_points, weekly_rank, cols_to_color):    
    pts_table = style_pts(weekly_points, False, cols_to_color)
    rank_table = style_pts(weekly_rank, True)
    return pts_table, rank_table



@st.cache_data(show_spinner=False)
def get_manager_profiles(h, p, selected_year, hit_cols, pit_cols):
    h_agg = h[h['season'] == selected_year].groupby('manager')[hit_cols].sum()
    p_agg = p[p['season'] == selected_year].groupby('manager')[pit_cols].sum()

    hit_scaled = ((h_agg - h_agg.min()) / (h_agg.max() - h_agg.min())).fillna(0)
    pit_scaled = ((p_agg - p_agg.min()) / (p_agg.max() - p_agg.min())).fillna(0)
    return hit_scaled, pit_scaled

def main():
    Navbar()

    st.title('⚾ Team Scoring')

if __name__ == '__main__':
    main()


tab1, tab2, tab3 = st.tabs(["This Week's Scoring", "This Season's Scoring", "Manager Profiles"])
team_week_df = load_team_week_points()
SEASON = 2026
WEEK = team_week_df[team_week_df['season'] == SEASON]['week'].max()
WEEK_TYPE = team_week_df[(team_week_df['season'] == SEASON) & (team_week_df['week'] == WEEK)]['week_type'].iloc[0]

with tab1:
    st.title("Latest Week Points Rankings")

    tmp = team_week_df[team_week_df['week_type'] == WEEK_TYPE].copy()

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
    st.plotly_chart(plot, width='stretch')

    hit = load_hitting_stats()
    hit_table = get_week_stat_summary(hit, SEASON, WEEK)
    hit_table = style_stat_summary(hit_table)
    st.header("This Week's Hitting Stats")
    st.dataframe(hit_table, width='content')
    
    pitch = load_pitching_stats()
    pitch_table = get_week_stat_summary(pitch, SEASON, WEEK)
    pitch_table = style_stat_summary(pitch_table)
    st.header("This Week's Pitching Stats")
    st.dataframe(pitch_table, width='content')


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

    pts_table, rank_table = build_season_tables(team_week_df, SEASON, pts_col)
    st.header(f"Season {label}")
    st.dataframe(pts_table, width='content')

    st.header(f"Season {label} Rank")
    st.dataframe(rank_table, width='content')

with tab3:
    st.title("Manager Stat Profiles")
    st.write("Radar charts comparing managers across key hitting and pitching stats. Stats are normalized 0-1 across all managers for the selected season")
    st.write("note that home run data does not exist prior to 2025")

    h = load_hitting_stats()
    p = load_pitching_stats()

    HIT_COLS = ['pts', 'R',  'RBI', 'BB', 'HR',   'TB',      'SB']
    PIT_COLS = ['pts', 'IP', 'K',   'QS', 'SV+H', 'K_per_IP'] 

    selected_year = st.selectbox("Select year", sorted(h['season'].unique(), reverse=True))
    managers = st.multiselect("Select managers", h['manager'].unique())

    hit_scaled, pit_scaled = get_manager_profiles(h, p, selected_year, HIT_COLS, PIT_COLS)

    fig = go.Figure()
    for manager in managers:
        if manager not in hit_scaled.index:
            continue
        ## hit compare
        categories = list(hit_scaled.columns)
        vals = hit_scaled.loc[manager].tolist()
        vals += [vals[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=categories + [categories[0]],
            fill='toself', name=manager
        ))

    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
                    title=f"Hitting Profiles")

    fig2 = go.Figure()
    for manager in managers:
        if manager not in pit_scaled.index:
            continue
        ## pitch compare
        categories = list(pit_scaled.columns)
        vals = pit_scaled.loc[manager].tolist()
        vals += [vals[0]]
        fig2.add_trace(go.Scatterpolar(
            r=vals, theta=categories + [categories[0]],
            fill='toself', name=manager
        ))

    fig2.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
                    title=f"Pitching Profiles")

    margin_dict = dict(t=25, b=25, l=25, r=25)
    fig.update_layout(margin=margin_dict)
    fig2.update_layout(margin=margin_dict)
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.plotly_chart(fig2, width='stretch')