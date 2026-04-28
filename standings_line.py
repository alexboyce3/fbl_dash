import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("Weekly Standings by Season")

df = pd.read_csv("standings_data.csv")
df = df[df['manager'] != '0']
df['manager'] = np.where(df['manager'] == 'Alex', 'Ulmer', df['manager'])


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