import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_utils import Navbar
from utils import expected_wins

st.set_page_config(page_title="Standings", layout="centered")

def main():
    Navbar()

    st.title(f'📈 Standings and Streaks')

if __name__ == '__main__':
    main()

tab1, tab2, tab3 = st.tabs(["Standings", "Streaks", "Expected Wins"])
## add tab for H2H
df = pd.read_csv("data/standings_data.csv")
df = df[df.manager.notnull()]

with tab1:

    curr_standings = df[(df['season'] == max(df['season']))].copy()
    curr_standings = curr_standings[curr_standings['week'] == max(curr_standings['week'])]
    curr_standings['points diff'] = curr_standings['points_for'] - curr_standings['points_against']
    curr_standings = curr_standings[['standings_rank', 'manager', 'wins', 'losses', 'games_back', 'points_for', 'points_against', 'points diff', 'streak']]
    curr_standings.rename(columns={'standings_rank': 'place',
                                'games_back': 'GB',
                                'points_for': 'PS',
                                'points_against': 'PA'}, inplace=True)
    for col in ['wins', 'losses', 'GB', 'PS', 'PA', 'points diff']:
        curr_standings[col] = curr_standings[col].astype(int)

    curr_standings = curr_standings.style.format(thousands=",")

    st.header("Current Standings")
    st.dataframe(curr_standings, width='content', hide_index=True)

    st.header("Weekly Standings by Season")
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

    st.plotly_chart(fig, width='stretch')

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
    st.plotly_chart(fig, width='stretch')

    ## make the loss labels more visible


    streak_table = (tmp[tmp['streak_length'] >= 6]
                [['season', 'manager', 'streak_type', 'streak_length']]
                .sort_values(by=['streak_length', 'streak_type'], ascending=[False, False])
                )
    streak_table_styled = streak_table.style.background_gradient(axis=0, gmap=streak_table["season"], cmap="Reds")
    streak_table_styled = streak_table_styled.set_properties(**{'text-align': 'center'})
    
    st.header("6+ Game Streaks")
    st.text("Last season Chris set a new longest winning streak record, while Andy tied the longest losing streak record")
    st.dataframe(streak_table_styled, width='content', hide_index=True)


with tab3:
    ## luck index
    final = df.groupby('season').apply(lambda x: x[x['week'] == x['week'].max()]).reset_index()
    actual = final[['season', 'manager', 'wins']]

    twp = pd.read_csv("data/team_week_points.csv")
    twp = twp.groupby(['season', 'week']).apply(expected_wins).reset_index()

    exp = (twp[twp['playoffs'] == 0]
        .groupby(['season', 'manager'])['expected_wins']
        .sum().reset_index())

    luck = exp.merge(actual, on=['season', 'manager'])
    luck['luck_index'] = luck['wins'] - luck['expected_wins']
    luck['luck_index'] = luck['luck_index'].round(1)


    selected_year = st.selectbox("Select year", sorted(luck['season'].unique()) + ['all'])
    if selected_year == 'all':
        t = luck.groupby(['manager', 'season'])['luck_index'].sum().reset_index()#.sort_values('luck_index')
        t['total_luck'] = t.groupby('manager')['luck_index'].transform('sum')
        plot_df = t.sort_values(['total_luck', 'season'], ascending=[True, True])
        selected_year = 'All Seasons'
    else:
        plot_df = luck[luck['season'] == selected_year].sort_values('luck_index')

    fig = px.bar(plot_df, x='manager', y='luck_index',
                color='season',
                labels={'luck_index': 'Actual W − Expected W'},
                title=f"Luck Index — {selected_year}")
    fig.add_hline(y=0, line_color='gray', line_dash='dash')
    fig.update_coloraxes(showscale=False)

    st.header("Luck Index")
    st.text("Luck Index = Actual Wins − Expected Wins")
    st.text("Expected wins = (number of managers you outscored) / (total managers - 1)")
    st.plotly_chart(fig, width='stretch')