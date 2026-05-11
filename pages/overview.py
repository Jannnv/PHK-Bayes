"""
Page 1: Overview TBC Nasional
KPI cards, Choropleth map (RR / Angka Penemuan toggle), Top/Bottom ranking, Insight box.
"""
import json
import os

from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from data.tbc_data_loader import (
    load_tbc_data, load_hyperparameter, load_diagnostik,
    COLORS, get_national_agg
)
from components.kpi_card import create_kpi_card
from components.insight_box import generate_insight_tbc
from components.chart_utils import apply_chart_styling, create_sparkline

# ── Load data ──────────────────────────────────────────────────────────────
DF   = load_tbc_data()
DF['Pulau'] = DF['Provinsi'].map(
    __import__('data.tbc_data_loader', fromlist=['PROVINSI_PULAU']).PROVINSI_PULAU
).fillna('Lainnya')
AGG  = get_national_agg(DF)
DIAG = load_diagnostik()
HYPER = load_hyperparameter()

# ── Load GeoJSON (tingkat provinsi, sudah ada di assets) ───────────────────
_ASSET_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
with open(os.path.join(_ASSET_DIR, 'indonesia_provinces.geojson'), 'r') as f:
    GEOJSON = json.load(f)

YEARS = sorted(DF['Tahun'].unique().tolist())


def _fmt(val, fmt):
    if fmt == 'rate':
        return f'{val:.1f}'
    elif fmt == 'rr':
        return f'{val:.3f}'
    elif fmt == 'persen':
        return f'{val:.1f}%'
    elif fmt == 'desimal2':
        return f'{val:.2f}'
    return str(val)


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
                html.H2('Overview TBC Nasional', className='page-title gradient-text'),
                html.P('Distribusi dan pola risiko TBC 34 provinsi berdasarkan model Bayesian ST-CAR',
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
                        html.Span('Peta TBC Indonesia', className='chart-title',
                                  style={'marginBottom': '0'}),
                        dbc.RadioItems(
                            id='ov-map-toggle',
                            options=[
                                {'label': 'RR (Model)', 'value': 'RR'},
                                {'label': 'Angka Penemuan /100k', 'value': 'Rate_per100k'},
                            ],
                            value='RR',
                            inline=True,
                            className='btn-group',
                            inputClassName='btn-check',
                            labelClassName='btn btn-outline-secondary btn-sm',
                            labelCheckedClassName='active',
                            style={'marginLeft': 'auto'},
                        ),
                    ], style={'display': 'flex', 'justifyContent': 'space-between',
                              'alignItems': 'center', 'marginBottom': '8px'}),
                    dcc.Graph(id='ov-choropleth', config={'displayModeBar': True, 'scrollZoom': True},
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
            'Dashboard TBC Indonesia | Model: Bayesian ST-CAR (INLA)',
            html.Br(),
            'Sumber Data: BPS, Kemenkes RI | Periode: 2020–2025',
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

    avg_rate  = df_y['Rate_per100k'].mean()
    avg_rr    = df_y['RR'].mean()
    avg_san   = df_y['Sanitasi'].mean()
    avg_air   = df_y['AirMinum'].mean()
    n_high_rr = int((df_y['RR'] > 1.0).sum())
    max_rr    = df_y['RR'].max()

    yoy_rate = _yoy(DF, 'Rate_per100k', tahun)
    yoy_rr   = _yoy(DF, 'RR', tahun)
    yoy_san  = _yoy(DF, 'Sanitasi', tahun)
    yoy_air  = _yoy(DF, 'AirMinum', tahun)

    # YoY for n_high_rr (count of provinces with RR > 1)
    if tahun > YEARS[0]:
        df_prev = DF[DF['Tahun'] == tahun - 1]
        n_prev = int((df_prev['RR'] > 1.0).sum())
        yoy_hrr = ((n_high_rr - n_prev) / n_prev) * 100 if n_prev != 0 else 0
        # YoY for max_rr
        prev_max = df_prev['RR'].max()
        yoy_maxrr = ((max_rr - prev_max) / prev_max) * 100 if prev_max != 0 else 0
    else:
        yoy_hrr = None
        yoy_maxrr = None

    sp_rate = _sparkline_vals(DF, 'Rate_per100k')
    sp_rr   = _sparkline_vals(DF, 'RR')
    sp_san  = _sparkline_vals(DF, 'Sanitasi')
    sp_air  = _sparkline_vals(DF, 'AirMinum')

    # Sparkline: jumlah provinsi RR>1 per tahun
    sp_hrr = [int((DF[DF['Tahun'] == y]['RR'] > 1.0).sum()) for y in YEARS]
    # Sparkline: max RR per tahun
    sp_maxrr = [float(DF[DF['Tahun'] == y]['RR'].max()) for y in YEARS]

    rr_progress = max(0, min(100, (1 - avg_rr) * 100 + 50))
    rate_progress = max(0, min(100, (1 - avg_rate / 150) * 100))

    cards = [
        create_kpi_card('rate', 'ANGKA PENEMUAN TBC', f'{avg_rate:.1f}/100k',
                        yoy_rate, sp_rate, '🫁', 'juta',
                        avg_rate > 80, rate_progress),
        create_kpi_card('rr', 'RATA-RATA RR NASIONAL', f'{avg_rr:.3f}',
                        yoy_rr, sp_rr, '📊', 'persen',
                        avg_rr > 1.0, rr_progress),
        create_kpi_card('hrr', 'PROVINSI RR > 1', f'{n_high_rr} Prov',
                        yoy_hrr, sp_hrr, '⚠️', 'desimal3',
                        n_high_rr > 17, (1 - n_high_rr / 34) * 100),
        create_kpi_card('maxrr', 'RR TERTINGGI', f'{max_rr:.3f}',
                        yoy_maxrr, sp_maxrr, '📈', 'desimal3',
                        max_rr > 1.5, max(0, (2 - max_rr) / 2 * 100)),
        create_kpi_card('san', 'SANITASI LAYAK', f'{avg_san:.1f}%',
                        yoy_san, sp_san, '🚿', 'persen',
                        False, avg_san),
        create_kpi_card('air', 'AIR MINUM LAYAK', f'{avg_air:.1f}%',
                        yoy_air, sp_air, '💧', 'persen',
                        False, avg_air),
    ]
    return cards


@callback(
    Output('ov-choropleth', 'figure'),
    Input('ov-year', 'value'),
    Input('ov-map-toggle', 'value'),
)
def update_map(tahun, map_col):
    df_y = DF[DF['Tahun'] == tahun].copy()

    # Use Provinsi_geo for matching GeoJSON
    df_y['_loc'] = df_y['Provinsi_geo'].fillna(df_y['Provinsi'])

    if map_col == 'RR':
        col_label = 'Relative Risk (RR)'
        cscale = [[0, '#ffffcc'], [0.3, '#a1dab4'], [0.6, '#2c7bb6'], [1, '#d7191c']]
        fmt = ':.3f'
        range_c = [df_y['RR'].min(), max(df_y['RR'].max(), 2.0)]
    else:
        col_label = 'Angka Penemuan per 100.000'
        cscale = [[0, '#440154'], [0.33, '#31688e'], [0.66, '#35b779'], [1, '#fde725']]
        fmt = ':.1f'
        range_c = [df_y['Rate_per100k'].min(), df_y['Rate_per100k'].max()]

    fig = px.choropleth_mapbox(
        df_y,
        geojson=GEOJSON,
        locations='_loc',
        featureidkey='properties.provinsi',
        color=map_col,
        color_continuous_scale=cscale,
        range_color=range_c,
        hover_name='Provinsi',
        hover_data={
            '_loc': False,
            'Rate_per100k': ':.1f',
            'RR': ':.3f',
            'Sanitasi': ':.1f',
            'AirMinum': ':.1f',
        },
        labels={
            'Rate_per100k': 'Angka Penemuan (/100k)',
            'RR': 'Relative Risk',
            'Sanitasi': 'Sanitasi Layak (%)',
            'AirMinum': 'Air Minum Layak (%)',
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
            title=dict(text=col_label, font=dict(family='Inter', color='#475569', size=11)),
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
    colors = ['#b8d4e3', '#9fc5d5', '#7caec4', '#5ba4a4', '#d94f4f']
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
    colors = ['#e0f2f1', '#b2dfdb', '#80cbc4', '#4db6ac', '#2e8b57']
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
            sel = click_data['points'][0].get('hovertext') or click_data['points'][0].get('location')
        except (IndexError, KeyError):
            pass
    return generate_insight_tbc(DF, tahun, sel)


@callback(Output('ov-diagnostik', 'children'), Input('ov-year', 'value'))
def update_diagnostik(_tahun):
    """Tampilkan diagnostik model (statis, tidak berubah per tahun)."""
    try:
        rows = []
        for _, row in DIAG.iterrows():
            col_name = row.iloc[0]
            col_val  = row.iloc[1]
            rows.append(html.Tr([
                html.Td(str(col_name), style={
                    'padding': '8px 12px', 'fontSize': '13px',
                    'color': '#475569', 'fontFamily': 'Inter',
                }),
                html.Td(f'{float(col_val):.3f}' if isinstance(col_val, (int, float)) else str(col_val),
                        style={
                    'padding': '8px 12px', 'fontSize': '13px', 'fontWeight': '600',
                    'color': '#2a7c8c', 'fontFamily': 'Inter', 'textAlign': 'right',
                }),
            ]))
        return html.Table(rows, style={'width': '100%', 'borderCollapse': 'collapse'})
    except Exception:
        return html.Div("Data diagnostik tidak tersedia.", style={'color': '#94a3b8', 'fontSize': '13px'})


@callback(Output('ov-hyperpar', 'children'), Input('ov-year', 'value'))
def update_hyperpar(_tahun):
    """Tampilkan hyperparameter posterior (statis)."""
    try:
        rows = []
        for _, row in HYPER.iterrows():
            param = row.iloc[0]
            mean  = row['mean'] if 'mean' in row.index else row.iloc[1]
            lo    = row['0.025quant'] if '0.025quant' in row.index else ''
            hi    = row['0.975quant'] if '0.975quant' in row.index else ''
            try:
                ci_str = f'({float(lo):.3f}, {float(hi):.3f})'
            except Exception:
                ci_str = '—'
            rows.append(html.Tr([
                html.Td(str(param), style={
                    'padding': '7px 12px', 'fontSize': '12px',
                    'color': '#475569', 'fontFamily': 'Inter',
                }),
                html.Td(f'{float(mean):.4f}' if mean is not None and str(mean) != 'nan' else '—',
                        style={
                    'padding': '7px 12px', 'fontSize': '13px', 'fontWeight': '600',
                    'color': '#2a7c8c', 'textAlign': 'right',
                }),
                html.Td(ci_str, style={
                    'padding': '7px 12px', 'fontSize': '11px',
                    'color': '#94a3b8', 'textAlign': 'right',
                }),
            ]))
        header = html.Tr([
            html.Th('Parameter', style={'padding': '8px 12px', 'fontSize': '11px',
                                         'color': '#94a3b8', 'fontWeight': '600',
                                         'borderBottom': '1px solid #e8eff4'}),
            html.Th('Mean', style={'padding': '8px 12px', 'fontSize': '11px',
                                    'color': '#94a3b8', 'fontWeight': '600',
                                    'textAlign': 'right', 'borderBottom': '1px solid #e8eff4'}),
            html.Th('95% CI', style={'padding': '8px 12px', 'fontSize': '11px',
                                      'color': '#94a3b8', 'fontWeight': '600',
                                      'textAlign': 'right', 'borderBottom': '1px solid #e8eff4'}),
        ])
        return html.Table([html.Thead(header), html.Tbody(rows)],
                          style={'width': '100%', 'borderCollapse': 'collapse'})
    except Exception as e:
        return html.Div(f"Error: {e}", style={'color': '#94a3b8', 'fontSize': '13px'})
