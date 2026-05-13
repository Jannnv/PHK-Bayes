"""
Page 1: Overview PHK Nasional
KPI cards, Choropleth map (RR toggle), Top/Bottom ranking, Insight box,
Diagnostik & Hyperparameter, Fixed Effects.
"""
import json
import os

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data.phk_data_loader import (
    load_phk_data, COLORS, get_national_agg
)
from components.kpi_card import create_kpi_card
from components.insight_box import generate_insight_phk
from components.chart_utils import apply_chart_styling, create_sparkline

# ── Load data ──────────────────────────────────────────────────────────────
DF     = load_phk_data()
AGG    = get_national_agg(DF)

# ── Load GeoJSON ───────────────────────────────────────────────────────────
_ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
with open(os.path.join(_ASSET_DIR, 'indonesia_provinces.geojson'), 'r') as f:
    GEOJSON = json.load(f)

YEARS = sorted(DF['Tahun'].unique().tolist())

# Orange colorscale for choropleth
RR_CSCALE = [
    [0.0,  '#FFF9C4'],
    [0.25, '#FFD54F'],
    [0.50, '#FF8F00'],
    [0.75, '#FF5500'],
    [1.0,  '#B71C1C'],
]


def _yoy(df, col, tahun, agg='mean'):
    curr = df[df['Tahun'] == tahun][col]
    prev = df[df['Tahun'] == tahun - 1][col]
    if tahun <= YEARS[0] or prev.empty:
        return 0
    c = curr.mean() if agg == 'mean' else curr.sum()
    p = prev.mean() if agg == 'mean' else prev.sum()
    return ((c - p) / p) * 100 if p != 0 else 0


def _sparkline_vals(df, col, agg='mean'):
    if agg == 'mean':
        return df.groupby('Tahun')[col].mean().values.tolist()
    return df.groupby('Tahun')[col].sum().values.tolist()


# ── Layout ─────────────────────────────────────────────────────────────────
def layout():
    return html.Div([
        # ── Header ──
        html.Div([
            html.Div([
                html.H2('Overview PHK Nasional', className='page-title gradient-text'),
                html.P('Distribusi dan pola risiko PHK 34 provinsi berdasarkan model Bayesian ST-CAR (2022–2025)',
                       className='page-subtitle'),
            ]),
            html.Div([
                dcc.Dropdown(
                    id='ov-year',
                    options=[{'label': str(y), 'value': y} for y in reversed(YEARS)],
                    value=YEARS[-1],
                    clearable=False,
                    style={'width': '120px'},
                    className='dash-dropdown',
                ),
            ], className='filter-bar'),
        ], className='page-header'),

        # ── KPI Cards ──
        dbc.Row(id='ov-kpi-row', className='g-3'),

        # ── Map + Rankings ──
        dbc.Row([
            # Map
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Span('Peta Relative Risk PHK Indonesia', className='chart-title',
                                  style={'marginBottom': '0'}),
                    ], style={'marginBottom': '8px'}),
                    dcc.Graph(id='ov-choropleth',
                              config={'displayModeBar': True, 'scrollZoom': True},
                              style={'height': '480px'}),
                ], className='glass-card glass-card-map'),
            ], lg=7, md=12, className='fade-in-up'),

            # Rankings
            dbc.Col([
                html.Div([
                    html.Div('🔴 5 Provinsi RR Tertinggi', className='chart-title'),
                    dcc.Graph(id='ov-top5', config={'displayModeBar': False},
                              style={'height': '220px'}),
                ], className='glass-card glass-card-chart', style={'marginBottom': '16px'}),
                html.Div([
                    html.Div('🟢 5 Provinsi RR Terendah', className='chart-title'),
                    dcc.Graph(id='ov-bottom5', config={'displayModeBar': False},
                              style={'height': '220px'}),
                ], className='glass-card glass-card-chart'),
            ], lg=5, md=12, className='fade-in-up'),
        ], className='g-3 section-gap'),

        # ── Insight Box ──
        html.Div(id='ov-insight', className='fade-in-up section-gap'),

        # ── Footer ──
        html.Div([
            'Dashboard PHK Indonesia | Model: Bayesian ST-CAR (CARBayesST)',
            html.Br(),
            'Sumber Data: BPS & Kemnaker RI | Periode: 2022–2025',
        ], className='dashboard-footer'),

    ], className='page-content')


# ═══════════════════════════════════════════════════════════════════════════
# CALLBACKS
# ═══════════════════════════════════════════════════════════════════════════

@callback(Output('ov-kpi-row', 'children'), Input('ov-year', 'value'))
def update_kpi(tahun):
    df_y = DF[DF['Tahun'] == tahun]
    if df_y.empty:
        return []

    avg_rr    = df_y['RR'].mean()
    total_phk = int(df_y['PHK'].sum())
    n_high_rr = int((df_y['RR'] > 1.0).sum())
    max_rr    = df_y['RR'].max()

    has_tpak = 'TPAK' in df_y.columns and df_y['TPAK'].notna().any()
    has_ipm  = 'IPM' in df_y.columns and df_y['IPM'].notna().any()

    avg_tpak = df_y['TPAK'].mean() if has_tpak else 0
    avg_ipm  = df_y['IPM'].mean() if has_ipm else 0

    yoy_rr   = _yoy(DF, 'RR', tahun)
    yoy_phk  = _yoy(DF, 'PHK', tahun, agg='sum')
    yoy_tpak = _yoy(DF, 'TPAK', tahun) if has_tpak else 0
    yoy_ipm  = _yoy(DF, 'IPM', tahun) if has_ipm else 0

    if tahun > YEARS[0]:
        df_prev = DF[DF['Tahun'] == tahun - 1]
        n_prev = int((df_prev['RR'] > 1.0).sum())
        yoy_hrr = ((n_high_rr - n_prev) / n_prev) * 100 if n_prev != 0 else 0
        prev_max = df_prev['RR'].max()
        yoy_maxrr = ((max_rr - prev_max) / prev_max) * 100 if prev_max != 0 else 0
    else:
        yoy_hrr = None
        yoy_maxrr = None

    sp_rr    = _sparkline_vals(DF, 'RR')
    sp_phk   = _sparkline_vals(DF, 'PHK', agg='sum')
    sp_hrr   = [int((DF[DF['Tahun'] == y]['RR'] > 1.0).sum()) for y in YEARS]
    sp_maxrr = [float(DF[DF['Tahun'] == y]['RR'].max()) for y in YEARS]
    sp_tpak  = _sparkline_vals(DF, 'TPAK') if has_tpak else [0]*len(YEARS)
    sp_ipm   = _sparkline_vals(DF, 'IPM') if has_ipm else [0]*len(YEARS)

    rr_progress  = max(0, min(100, (2 - avg_rr) / 2 * 100))
    phk_progress = max(0, min(100, 100 - (total_phk / 50000)))

    cards = [
        create_kpi_card('rr', 'RATA-RATA RR NASIONAL', f'{avg_rr:.3f}',
                        yoy_rr, sp_rr, '📊', 'persen',
                        avg_rr > 1.0, rr_progress),
        create_kpi_card('phk', 'TOTAL PHK', f'{total_phk:,}',
                        yoy_phk, sp_phk, '👷', 'juta',
                        total_phk > 30000, phk_progress),
        create_kpi_card('hrr', 'PROVINSI RR > 1', f'{n_high_rr} Prov',
                        yoy_hrr, sp_hrr, '⚠️', 'desimal3',
                        n_high_rr > 17, (1 - n_high_rr / 34) * 100),
        create_kpi_card('maxrr', 'RR TERTINGGI', f'{max_rr:.3f}',
                        yoy_maxrr, sp_maxrr, '📈', 'desimal3',
                        max_rr > 1.5, max(0, (3 - max_rr) / 3 * 100)),
        create_kpi_card('tpak', 'RATA-RATA TPAK', f'{avg_tpak:.1f}%',
                        yoy_tpak, sp_tpak, '👥', 'persen',
                        False, avg_tpak),
        create_kpi_card('ipm', 'RATA-RATA IPM', f'{avg_ipm:.2f}',
                        yoy_ipm, sp_ipm, '🎓', 'kota',
                        False, avg_ipm),
    ]
    return cards


@callback(Output('ov-choropleth', 'figure'), Input('ov-year', 'value'))
def update_map(tahun):
    df_y = DF[DF['Tahun'] == tahun].copy()
    df_y['_loc'] = df_y['Provinsi']

    rr_min = max(0, df_y['RR'].min())
    rr_max = max(df_y['RR'].max(), 2.0)

    hover_data = {
        '_loc': False,
        'PHK': ':,',
        'RR': ':.3f',
    }
    if 'TPAK' in df_y.columns:
        hover_data['TPAK'] = ':.1f'
    if 'IPM' in df_y.columns:
        hover_data['IPM'] = ':.2f'

    fig = px.choropleth_mapbox(
        df_y,
        geojson=GEOJSON,
        locations='_loc',
        featureidkey='properties.provinsi',
        color='RR',
        color_continuous_scale=RR_CSCALE,
        range_color=[rr_min, rr_max],
        hover_name='Provinsi',
        hover_data=hover_data,
        labels={
            'PHK': 'Jumlah PHK',
            'RR': 'Relative Risk',
            'TPAK': 'TPAK (%)',
            'IPM': 'IPM',
        },
        mapbox_style='carto-positron',
        center={'lat': -2.5, 'lon': 118},
        zoom=3.8,
        opacity=0.85,
    )

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            title=dict(text='Relative Risk (RR)',
                       font=dict(family='Inter', color='#475569', size=11)),
            tickfont=dict(family='Inter', color='#94a3b8', size=10),
            bgcolor='rgba(255,255,255,0.85)',
            outlinecolor='#d1dce6',
            len=0.6, thickness=12, x=0.98, xanchor='right',
        ),
        hoverlabel=dict(
            bgcolor='#ffffff', bordercolor='#d1dce6',
            font=dict(family='Inter', size=12, color='#1e293b'),
        ),
    )
    return fig


@callback(Output('ov-top5', 'figure'), Input('ov-year', 'value'))
def update_top5(tahun):
    df_y = DF[DF['Tahun'] == tahun].nlargest(5, 'RR').sort_values('RR')
    colors = ['#FFD54F', '#FFB300', '#FF8F00', '#FF5500', '#CC0000']
    fig = go.Figure(go.Bar(
        x=df_y['RR'], y=df_y['Provinsi'], orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        text=df_y['RR'].apply(lambda x: f'{x:.3f}'),
        textposition='outside',
        textfont=dict(family='Inter', size=11, color='#475569'),
        hovertemplate='<b>%{y}</b><br>RR: %{x:.3f}<extra></extra>',
    ))
    apply_chart_styling(fig)
    fig.update_layout(
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(tickfont=dict(family='Inter', size=11, color='#475569'), automargin=True),
        height=200, showlegend=False,
    )
    return fig


@callback(Output('ov-bottom5', 'figure'), Input('ov-year', 'value'))
def update_bottom5(tahun):
    df_y = DF[DF['Tahun'] == tahun].nsmallest(5, 'RR').sort_values('RR', ascending=False)
    colors = ['#FFF9C4', '#FFF176', '#FFEE58', '#FDD835', '#F9A825']
    fig = go.Figure(go.Bar(
        x=df_y['RR'], y=df_y['Provinsi'], orientation='h',
        marker=dict(color=colors, line=dict(width=0)),
        text=df_y['RR'].apply(lambda x: f'{x:.3f}'),
        textposition='outside',
        textfont=dict(family='Inter', size=11, color='#475569'),
        hovertemplate='<b>%{y}</b><br>RR: %{x:.3f}<extra></extra>',
    ))
    apply_chart_styling(fig)
    fig.update_layout(
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(tickfont=dict(family='Inter', size=11, color='#475569'), automargin=True),
        height=200, showlegend=False,
    )
    return fig


@callback(
    Output('ov-insight', 'children'),
    Input('ov-year', 'value'),
    Input('ov-choropleth', 'clickData'),
)
def update_insight(tahun, click_data):
    sel = None
    if click_data and 'points' in click_data:
        try:
            sel = (click_data['points'][0].get('hovertext') or
                   click_data['points'][0].get('location'))
        except (IndexError, KeyError):
            pass
    return generate_insight_phk(DF, tahun, sel)


