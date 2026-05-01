import pandas as pd
import plotly.express as px


def plot_points(df, pts_col, label, season, week):
    highlight_mask = (df['season'] == season) & (df['week'] == week)
    df['_dummy_x'] = 0
    week_type = df['week_type'].iloc[0]
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
    fig.update_layout(title=f"{label} by Week ({week_type} weeks only)")
    return fig


def heatmap_cols(df, desc_cols):
    styled = df.style
    for col in df.columns:
        gmap = None
        if col in desc_cols:
            gmap = -df[col]
        styled = styled.background_gradient(subset=[col],
                                            cmap='RdYlGn',
                                            gmap=gmap)
    styled = styled.set_properties(**{'text-align': 'center'})
    styled = styled.format(precision=2)
    return styled


def stat_summary(df, season, week):
    if 'SB' in df.columns:
        desc_cols = []
    else:
        desc_cols=['H', 'ER', 'BB', 'ERA', 'WHIP']

    hm_df = df.copy()
    hm_df = hm_df[(hm_df.season == season)
                  & (hm_df.week == week)].sort_values(by='pts', ascending=False)
    hm_df.set_index('manager', inplace=True)

    start_col = hm_df.columns.get_loc('pts')
    hm_df = hm_df.iloc[:, start_col:]

    float_cols = ['ERA', 'WHIP', 'K_per_IP']
    for col in hm_df.columns:
        if col in float_cols:
            hm_df[col] = hm_df[col].round(2)
        else:
            hm_df[col] = hm_df[col].astype(int)
    styled = heatmap_cols(hm_df, desc_cols)

    return styled


def something(team_week_points, SEASON):
    
    team_pts = (team_week_points[(team_week_points['season'] == SEASON)]
                .groupby('manager')
                [['team_points', 'hitting_points', 'pitching_points']]
                .sum().sort_values(by='team_points', ascending=False)
                )
    return team_pts
