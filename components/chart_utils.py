"""
Chart Utilities — Light Professional Theme
Shared Plotly figure styling for the dashboard.
"""
import plotly.graph_objects as go


# ── Light theme chart palette ──
CHART_COLORS = ['#3d8b8a', '#5ba4a4', '#7ab8b8', '#4a8fa8', '#7caec4',
                '#9fc5d5', '#b8d4e3', '#80cbc4', '#26a69a', '#1e3a4f']


def apply_chart_styling(fig, title=None):
    """Apply consistent light theme styling to a Plotly figure."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family='Inter, sans-serif',
            color='#475569',
            size=12,
        ),
        title=dict(
            text=title,
            font=dict(family='Inter', size=15, color='#1e293b'),
            x=0,
        ) if title else None,
        margin=dict(l=40, r=20, t=30, b=40),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5,
            font=dict(color='#475569', size=11),
            bgcolor='rgba(0,0,0,0)',
        ),
        xaxis=dict(
            gridcolor='#e8eff4',
            zerolinecolor='#d1dce6',
            tickfont=dict(color='#94a3b8', size=11),
            linecolor='#d1dce6',
        ),
        yaxis=dict(
            gridcolor='#e8eff4',
            zerolinecolor='#d1dce6',
            tickfont=dict(color='#94a3b8', size=11),
            linecolor='#d1dce6',
        ),
        hoverlabel=dict(
            bgcolor='#ffffff',
            bordercolor='#d1dce6',
            font=dict(family='Inter', size=12, color='#1e293b'),
        ),
    )
    return fig


def create_sparkline(data, color='#4db6ac', height=30):
    """Create a minimal sparkline figure for KPI cards."""
    fig = go.Figure(go.Scatter(
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.1)',
        hoverinfo='skip',
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=height,
        showlegend=False,
    )

    return fig
