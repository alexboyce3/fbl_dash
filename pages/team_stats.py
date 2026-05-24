import streamlit as st
import pandas as pd
from utils import stat_summary, plot_points, style_pts
from streamlit_utils import Navbar
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(page_title="Team Scoring", layout="centered")

def main():
    Navbar()

    st.title(f'⚾ Team Scoring')

if __name__ == '__main__':
    main()


tab1, tab2, tab3 = st.tabs(["This Week's Scoring", "This Season's Scoring", "Manager Profiles"])
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

with tab3:
    st.title("Manager Stat Profiles")
    st.write("Radar charts comparing managers across key hitting and pitching stats. Stats are normalized 0-1 across all managers for the selected season, so higher is always better.")

    h = pd.read_csv("data/hitting_stats.csv")
    p = pd.read_csv("data/pitching_stats.csv")

    HIT_COLS = ['pts', 'R',  'RBI', 'BB', 'HR',   'TB',      'SB']
    PIT_COLS = ['pts', 'IP', 'K',   'QS', 'SV+H', 'K_per_IP'] 

    selected_year = st.selectbox("Select year", sorted(h['season'].unique(), reverse=True))
    managers = st.multiselect("Select managers", h['manager'].unique())

    h_agg = h[h['season'] == selected_year].groupby('manager')[HIT_COLS].sum()
    p_agg = p[p['season'] == selected_year].groupby('manager')[PIT_COLS].sum()

    scaler = MinMaxScaler()
    hit_scaled = pd.DataFrame(scaler.fit_transform(h_agg), index=h_agg.index, columns=h_agg.columns)
    pit_scaled = pd.DataFrame(scaler.fit_transform(p_agg), index=p_agg.index, columns=p_agg.columns)

    fig = go.Figure()
    for manager in managers:
        ## hit compare
        categories = list(hit_scaled.columns)
        vals = hit_scaled.loc[manager].tolist()
        vals += [vals[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=categories + [categories[0]],
            fill='toself', name=manager
        ))

    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
                    title=f"Manager Stat Profile - {selected_year}")

    fig2 = go.Figure()
    for manager in managers:
        ## pitch compare
        categories = list(pit_scaled.columns)
        vals = pit_scaled.loc[manager].tolist()
        vals += [vals[0]]
        fig2.add_trace(go.Scatterpolar(
            r=vals, theta=categories + [categories[0]],
            fill='toself', name=manager
        ))

    fig2.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 1])),
                    title=f"Manager Stat Profile - {selected_year}")

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.plotly_chart(fig2, use_container_width=True)