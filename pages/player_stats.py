import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_utils import Navbar

st.set_page_config(page_title="Player Scoring", layout="centered")

def main():
    Navbar()

    st.title(f'⚾ Player Scoring')

if __name__ == '__main__':
    main()

def load_data():
    player = pd.read_csv("data/player_top.csv")
    team = pd.read_csv("data/team_week_points.csv")
    detail = pd.read_csv("data/player_stat_detail.csv")

    week_meta = team[["season", "week", "week_type", "playoffs"]].drop_duplicates()
    player = player.merge(week_meta, on=["season", "week"], how="left")
    player = player[player["starting"] == 1]
    return player, detail

player, detail = load_data()

SEASONS = sorted(player["season"].unique(), reverse=True)
WEEK_TYPES = ["normal", "long", "short"]
MANAGERS = sorted(player["manager_name"].dropna().unique())

tab1, tab2 = st.tabs(["Top Player Weeks", "Player Scoring Profile"])

### top N player weeks
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    wt_2 = col1.selectbox("Week type", WEEK_TYPES, key="wt")
    top_n = col2.selectbox("Show top N", [10, 25, 50], key="n")
    season = col3.selectbox("Season", SEASONS + ['all'], key="season")
    player_type = col4.selectbox("Player Type", ["Hitters", "Pitchers"], key='ptype')

    if season != 'all':
        tmp = player[player["season"] == int(season)].copy()
    else:
        tmp = player.copy()

    if player_type == 'Hitters':
        ptype = 'B'
    else:
        ptype = 'P'

    df = (tmp[(tmp["week_type"] == wt_2) & (tmp["player_type"] == ptype)]
            [["player_name", "pts", "manager_name", "season", "week"]])

    df = df.nlargest(top_n, "pts").reset_index(drop=True)

    df.index += 1
    df.columns = ["Player", "Points", "Manager", "Season", "Week"]
    df = df.reset_index().rename(columns={"index": "Rank"})

    st.dataframe(df, use_container_width=True, hide_index=True)

## player profile
with tab2:
    col1, col2 = st.columns(2)
    season = col1.selectbox("Season", SEASONS + ['all'], key="season2")
    player_type = col2.selectbox("Player Type", ["Hitters", "Pitchers"], key='ptype2')

    h_bins = [-np.inf, 0.4, 9.9, 19.9, 29.9, 39.9, np.inf]
    h_names = ['nothing', 'bad', 'fine', 'solid', 'good', 'great'] ## 3% / 19% / 36% / 28% / 11% / 4%

    p_bins = [-np.inf, -0.1, 0.1, 9.9, 19.9, 29.9, 44.9, np.inf]
    p_names = ['negative', 'nothing', 'bad', 'fine', 'solid', 'good', 'great'] ## 2.5% / 5% / 17% / 30% / 30% / 12% / 4%

    if player_type == 'Hitters':
        ptype = 'B'
        bins = h_bins
        names = h_names
    else:
        ptype = 'P'
        bins = p_bins
        names = p_names

    tmp = player[(player["week_type"] == "normal")
                 & (player["player_type"] == ptype)
                 & (player["starting"] == 1)
                 ].copy()

    if season != "all":
        tmp = tmp[tmp["season"] == season]

    tmp['scoring_group'] = pd.cut(tmp['pts'], bins, labels=names)
    tmp = tmp.groupby(['manager_name', 'scoring_group']).size().reset_index().rename(columns={0: 'count'})

    fig = px.bar(tmp,
                x="manager_name",
                y="count",
                color='scoring_group'
                )
    fig.update_layout(xaxis={'categoryarray':list(tmp['manager_name'].drop_duplicates())})
    st.plotly_chart(fig, use_container_width=True)
