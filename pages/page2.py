## placeholder

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

tab1, tab2 = st.tabs(["Points Rankings", "Stats Rankings"])

def plot_points(df, pts_col, label, season, week):
    highlight_mask = (df['season'] == season) & (df['week'] == week)
    df['_dummy_x'] = 0
    ht = 'Season: %{customdata[0]}\
        <br>Week: %{customdata[1]}\
            <br>Playoffs: %{customdata[3]}\
                <br>Manager: %{customdata[2]}\
                    <br>Points: %{y:.2f}<extra></extra>'

    fig = px.strip(df,
                x='_dummy_x',
                y=pts_col,
                color_discrete_sequence=['gray'],
                )
    fig.data[0].hovertemplate = ht
    fig.data[0].customdata = df[['season', 'week', 'manager', 'playoffs']].values


    # Overlay highlights in red
    fig.add_scatter(
        x=df.loc[highlight_mask, '_dummy_x'],
        y=df.loc[highlight_mask, pts_col],
        mode='markers',
        marker=dict(color='red', size=12, symbol='star'),
        hovertemplate=ht,
        customdata=df.loc[highlight_mask, ['season', 'week', 'manager', 'playoffs']].values,

    )
    fig.update_xaxes(range=[-0.2, 0.2], showticklabels=False, title_text='')
    fig.update_layout(showlegend=False)
    fig.update_yaxes(title_text=label)
    fig.update_layout(title=f"{label} by Week ({tmp.week_type.iloc[0]} weeks only)")
    return fig

with tab1:
    st.title("Latest Week Points Rankings")

    df = pd.read_csv("data/team_week_points.csv")
    SEASON = 2026
    WEEK = df[df['season'] == SEASON]['week'].max()
    WEEK_TYPE = df[(df['season'] == SEASON) & (df['week'] == WEEK)]['week_type'].iloc[0]
    tmp = df[df['week_type'] == WEEK_TYPE].copy()

    team_plot = plot_points(tmp, 'team_points', 'Team Points', SEASON, WEEK)
    st.plotly_chart(team_plot, use_container_width=True)
    hitting_plot = plot_points(tmp, 'hitting_points', 'Hitting Points', SEASON, WEEK)
    st.plotly_chart(hitting_plot, use_container_width=True)
    pitching_plot = plot_points(tmp, 'pitching_points', 'Pitching Points', SEASON, WEEK)
    st.plotly_chart(pitching_plot, use_container_width=True)

with tab2:
    st.title("Latest Week Stats Rankings")
