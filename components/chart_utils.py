"""
Chart Utilities — Orange Gradient Theme
Shared Plotly figure styling for the PHK dashboard.
"""
import plotly.graph_objects as go


# ── Orange gradient chart palette ──
CHART_COLORS = ['#FFC800', '#FFB300', '#FF9E00', '#FF8F00', '#FF7200',
                '#FF5500', '#FF3D00', '#FF0000', '#E60000', '#CC0000']


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


def create_sparkline(data, color='#FF5500', height=30):
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
