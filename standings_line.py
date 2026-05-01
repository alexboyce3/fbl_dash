import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_utils import Navbar

st.set_page_config(page_title="Standings", layout="centered")

def main():
    Navbar()

    st.title(f'📈 Standings and Streaks')

if __name__ == '__main__':
    main()

tab1, tab2 = st.tabs(["Standings", "Streaks"])
## add tab for H2H
df = pd.read_csv("data/standings_data.csv")
df = df[df['manager'] != '0']
df['manager'] = np.where(df['manager'] == 'Alex', 'Ulmer', df['manager'])

with tab1:
    st.title("Weekly Standings by Season")

    years = sorted(df["season"].unique(), reverse=True)
    selected_year = st.selectbox("Select year", years)
    filtered = df[df["season"] == selected_year].sort_values(by='manager')

    fig = px.line(
        filtered,
        x="week",
        y="standings_rank",
        line_group="manager",
        color='manager',
        color_discrete_sequence=px.colors.qualitative.G10,
        labels={"week": "Week", 'standings_rank': 'standing'},
        title=f"Standings by Week — {selected_year}"
    )
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(type='category')

    st.plotly_chart(fig, use_container_width=True)

with tab2:
    tmp = df.copy()
    tmp['streak_type'] = tmp['streak'].str[0]
    tmp2 = tmp[['season', 'week', 'manager', 'streak_type']].copy()
    tmp2['week'] = tmp2['week'] - 1
    tmp2.rename(columns={'streak_type': 'next_streak_type'}, inplace=True)
    tmp = tmp.merge(tmp2, on=['season', 'week', 'manager'], how='left')
    tmp['max_streak'] = np.where(tmp['streak_type'] != tmp['next_streak_type'], tmp['streak'], None)
    tmp['max_streak'] = np.where(tmp['max_streak'].isin(['L1', 'W1']), None, tmp['max_streak'])
    tmp = tmp[tmp['max_streak'].notna()]
    tmp['streak_length'] = tmp['max_streak'].str[1:].astype(int)
    
    streak_counts = tmp.groupby(['streak_type', 'streak_length']).size().reset_index().rename(columns={0: 'number'})
    streak_counts.sort_values('number', inplace=True)
    fig = px.funnel(streak_counts, x='streak_length', y='number', color='streak_type',
                        color_discrete_sequence=px.colors.qualitative.G10,
                        )
    
    st.header("Number of Streaks by Length, Type")
    st.plotly_chart(fig, use_container_width=True)

    ## make the loss labels more visible


    streak_table = (tmp[tmp['streak_length'] >= 6]
                [['season', 'manager', 'streak_type', 'streak_length']]
                .sort_values(by=['streak_length', 'streak_type'], ascending=[False, False])
                )
    streak_table_styled = streak_table.style.background_gradient(axis=0, gmap=streak_table["season"], cmap="Reds")
    streak_table_styled = streak_table_styled.set_properties(**{'text-align': 'center'})
    
    st.header("6+ Game Streaks")
    st.text("Last season Chris set a new longest winning streak record, while Andy tied the longest losing streak record")
    st.dataframe(streak_table_styled, use_container_width=False, hide_index=True)