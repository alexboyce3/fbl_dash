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

@st.cache_data
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



col1, col2, col3 = st.columns(3)
wt_2 = col1.selectbox("Week type", WEEK_TYPES, key="wt_2")
top_n = col2.selectbox("Show top N", [10, 25, 50], key="n_2")
season = col3.selectbox("Season", SEASONS + ['all'], key="season_2")

tab_h, tab_p = st.tabs(["Hitters", "Pitchers"])

if season != 'all':
    tmp = player[player["season"] == int(season)].copy()
else:
    tmp = player.copy()

for tab, ptype, label in [(tab_h, "B", "Hitter"), (tab_p, "P", "Pitcher")]:
    with tab:
        df = (tmp[(tmp["week_type"] == wt_2) & (tmp["player_type"] == ptype)]
                [["player_name", "pts", "manager_name", "season", "week"]])

        df = df.nlargest(top_n, "pts").reset_index(drop=True)

        df.index += 1
        df.columns = ["Player", "Points", "Manager", "Season", "Week"]
        df = df.reset_index().rename(columns={"index": "Rank"})

        st.dataframe(df, use_container_width=False, hide_index=True)
