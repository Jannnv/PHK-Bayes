"""
Page 2: Tren & Analisis PHK
Tren RR temporal, ranking provinsi, scatter TPAK/IPM vs RR, fixed effects forest plot, data table.
"""
from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from data.phk_data_loader import (
    load_phk_data, load_fixed_effects, COLORS, get_national_agg
)
from components.chart_utils import apply_chart_styling, CHART_COLORS

# ── Load data ───────────────────────────────────────────────────────────────
DF       = load_phk_data()
AGG      = get_national_agg(DF)
FIXED_FX = load_fixed_effects()
PROVINSI_LIST = sorted(DF['Provinsi'].unique().tolist())
YEARS         = sorted(DF['Tahun'].unique().tolist())

# Kovariat available
_has_tpak = 'TPAK' in DF.columns and DF['TPAK'].notna().any()
_has_ipm  = 'IPM' in DF.columns and DF['IPM'].notna().any()

KOVARIAT_OPTIONS = []
if _has_tpak:
    KOVARIAT_OPTIONS.append({'label': 'TPAK (%)', 'value': 'TPAK'})
if _has_ipm:
    KOVARIAT_OPTIONS.append({'label': 'IPM', 'value': 'IPM'})
if not KOVARIAT_OPTIONS:
    KOVARIAT_OPTIONS = [{'label': 'PHK (Observasi)', 'value': 'PHK'}]

_default_kov = KOVARIAT_OPTIONS[0]['value']

# Orange gradient for ranking
_TOP_COLORS    = ['#FFD54F', '#FFB300', '#FF9E00', '#FF7200', '#FF5500',
                  '#FF3D00', '#FF2600', '#FF0000', '#E60000', '#CC0000']
_BOTTOM_COLORS = ['#FFF9C4', '#FFF176', '#FFEE58', '#FDD835', '#FBC02D',
                  '#F9A825', '#F57F17', '#FF8F00', '#FF6F00', '#E65100']


def layout():
    return html.Div([
        # ── Header ──
        html.Div([
            html.Div([
                html.H2('Tren & Analisis PHK', className='page-title gradient-text'),
                html.P('Perkembangan temporal RR, korelasi kovariat, dan hasil model Bayesian ST-CAR',
                       className='page-subtitle'),
            ]),
        ], className='page-header'),

        # ── Filter Bar ──
        html.Div([
            html.Div([
                html.Label('Rentang Tahun:', style={
                    'fontSize': '11px', 'color': '#94a3b8', 'fontFamily': 'Inter',
                    'textTransform': 'uppercase', 'letterSpacing': '2px', 'marginBottom': '8px',
                }),
                dcc.RangeSlider(
                    id='tr-year-slider',
                    min=YEARS[0], max=YEARS[-1], step=1,
                    marks={y: {'label': str(y), 'style': {'color': '#94a3b8'}} for y in YEARS},
                    value=[YEARS[0], YEARS[-1]],
                    className='teal-slider',
                ),
            ], style={'flex': '2', 'minWidth': '260px'}),

            html.Div([
                html.Label('Sorot Provinsi:', style={
                    'fontSize': '11px', 'color': '#94a3b8', 'fontFamily': 'Inter',
                    'textTransform': 'uppercase', 'letterSpacing': '2px', 'marginBottom': '8px',
                }),
                dcc.Dropdown(
                    id='tr-prov-dropdown',
                    options=[{'label': p, 'value': p} for p in PROVINSI_LIST],
                    value=[], multi=True,
                    placeholder='Pilih provinsi (maks 5)...',
                    className='dash-dropdown',
                ),
            ], style={'flex': '2', 'minWidth': '250px'}),

            html.Div([
                html.Label('Tampilkan:', style={
                    'fontSize': '11px', 'color': '#94a3b8', 'fontFamily': 'Inter',
                    'textTransform': 'uppercase', 'letterSpacing': '2px', 'marginBottom': '8px',
                }),
                dbc.RadioItems(
                    id='tr-metric-toggle',
                    options=[
                        {'label': 'RR', 'value': 'RR'},
                        {'label': 'PHK (Observasi)', 'value': 'PHK'},
                    ],
                    value='RR', inline=True,
                    className='btn-group',
                    inputClassName='btn-check',
                    labelClassName='btn btn-outline-secondary btn-sm',
                    labelCheckedClassName='active',
                ),
            ], style={'flex': '1', 'minWidth': '200px'}),
        ], className='glass-card', style={
            'display': 'flex', 'gap': '24px', 'alignItems': 'flex-end',
            'flexWrap': 'wrap', 'padding': '20px 24px', 'marginBottom': '24px',
        }),

        # ── Line Chart ──
        html.Div([
            html.Div(id='tr-line-title', className='chart-title'),
            dcc.Graph(id='tr-line-chart', config={'displayModeBar': True},
                      style={'height': '400px'}),
        ], className='glass-card fade-in-up'),

        # ── Ranking + Scatter ──
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div([
                        html.Span('Ranking Provinsi berdasarkan RR', className='chart-title',
                                  style={'marginBottom': '0'}),
                        dbc.RadioItems(
                            id='tr-ranking-toggle',
                            options=[
                                {'label': 'Tertinggi', 'value': 'top'},
                                {'label': 'Terendah', 'value': 'bottom'},
                            ],
                            value='top', inline=True,
                            className='btn-group',
                            inputClassName='btn-check',
                            labelClassName='btn btn-outline-secondary btn-sm',
                            labelCheckedClassName='active',
                            style={'marginLeft': 'auto'},
                        ),
                    ], style={'display': 'flex', 'justifyContent': 'space-between',
                              'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '8px',
                              'marginBottom': '12px'}),
                    dcc.Graph(id='tr-ranking-bar', config={'displayModeBar': False},
                              style={'height': '400px'}),
                ], className='glass-card'),
            ], lg=5, md=12),

            dbc.Col([
                html.Div([
                    html.Div([
                        html.Span('Korelasi Kovariat vs RR', className='chart-title',
                                  style={'marginBottom': '0'}),
                        dcc.Dropdown(
                            id='tr-scatter-x',
                            options=KOVARIAT_OPTIONS,
                            value=_default_kov, clearable=False,
                            className='dash-dropdown',
                            style={'width': '180px', 'marginLeft': 'auto'},
                        ),
                    ], style={'display': 'flex', 'justifyContent': 'space-between',
                              'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '8px',
                              'marginBottom': '12px'}),
                    dcc.Graph(id='tr-scatter', config={'displayModeBar': True},
                              style={'height': '400px'}),
                ], className='glass-card'),
            ], lg=7, md=12),
        ], className='g-3 section-gap'),

        # ── Forest Plot Fixed Effects ──
        html.Div([
            html.Div('🌲 Forest Plot — Fixed Effects (β)', className='chart-title'),
            dcc.Graph(id='tr-fixed-effects', config={'displayModeBar': False},
                      style={'height': '300px'}),
        ], className='glass-card section-gap fade-in-up'),

        # ── Data Table ──
        html.Div([
            html.Div([
                html.Span('📋 Data per Provinsi', className='chart-title'),
                html.Span(' — Klik header untuk sort',
                          style={'fontSize': '11px', 'color': '#64748b', 'marginLeft': '8px'}),
            ], style={'marginBottom': '16px'}),
            html.Div(id='tr-data-table'),
        ], className='glass-card section-gap fade-in-up'),

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

@callback(
    Output('tr-line-chart', 'figure'),
    Output('tr-line-title', 'children'),
    Input('tr-year-slider', 'value'),
    Input('tr-prov-dropdown', 'value'),
    Input('tr-metric-toggle', 'value'),
)
def update_line(year_range, sel_provs, metric):
    y0, y1 = year_range
    metric_col = 'rata_rr' if metric == 'RR' else 'rata_phk'
    label = 'Rata-rata RR Nasional' if metric == 'RR' else 'Rata-rata PHK Nasional'
    title = f'Tren {label} ({y0}–{y1})'
    y_label = 'Relative Risk (RR)' if metric == 'RR' else 'Jumlah PHK'

    agg = AGG[(AGG['Tahun'] >= y0) & (AGG['Tahun'] <= y1)]

    fig = go.Figure()

    show_dashed = bool(sel_provs)
    fig.add_trace(go.Scatter(
        x=agg['Tahun'], y=agg[metric_col],
        name='Nasional', mode='lines+markers',
        line=dict(color='#FF5500', width=3,
                  dash='dash' if show_dashed else 'solid'),
        marker=dict(size=7, color='#FF5500'),
        fill='tozeroy' if not show_dashed else None,
        fillcolor='rgba(255,85,0,0.08)' if not show_dashed else None,
    ))

    if metric == 'RR':
        fig.add_hline(y=1.0, line_dash='dot', line_color='#94a3b8',
                      annotation_text='RR = 1 (Rata-rata Nasional)',
                      annotation_position='bottom right',
                      annotation_font=dict(color='#94a3b8', size=10, family='Inter'))

    if sel_provs:
        col_map = {'RR': 'RR', 'PHK': 'PHK'}
        for i, prov in enumerate(sel_provs[:5]):
            df_p = DF[(DF['Provinsi'] == prov) &
                      (DF['Tahun'] >= y0) & (DF['Tahun'] <= y1)]
            fig.add_trace(go.Scatter(
                x=df_p['Tahun'], y=df_p[col_map[metric]],
                name=prov, mode='lines+markers',
                line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
                marker=dict(size=5),
            ))

    apply_chart_styling(fig, '')
    fig.update_layout(
        hovermode='x unified',
        xaxis=dict(dtick=1),
        yaxis=dict(title=dict(text=y_label, font=dict(size=11, color='#475569'))),
        margin=dict(l=50, r=20, t=20, b=60),
        legend=dict(y=-0.25),
    )
    return fig, title


@callback(
    Output('tr-ranking-bar', 'figure'),
    Input('tr-year-slider', 'value'),
    Input('tr-ranking-toggle', 'value'),
)
def update_ranking(year_range, toggle):
    tahun = year_range[1]
    df_y  = DF[DF['Tahun'] == tahun]
    if toggle == 'top':
        df_p   = df_y.nlargest(10, 'RR').sort_values('RR')
        colors = _TOP_COLORS
    else:
        df_p   = df_y.nsmallest(10, 'RR').sort_values('RR', ascending=False)
        colors = _BOTTOM_COLORS

    n = len(df_p)
    color_list = [colors[int(i * (len(colors) - 1) / max(n - 1, 1))] for i in range(n)]

    fig = go.Figure(go.Bar(
        x=df_p['RR'], y=df_p['Provinsi'], orientation='h',
        marker=dict(color=color_list),
        text=df_p['RR'].apply(lambda x: f'{x:.3f}'),
        textposition='outside',
        textfont=dict(family='Inter', size=11, color='#475569'),
        hovertemplate='<b>%{y}</b><br>RR: %{x:.3f}<extra></extra>',
    ))
    apply_chart_styling(fig)
    fig.add_vline(x=1.0, line_dash='dot', line_color='#94a3b8',
                  annotation_text='RR=1', annotation_font=dict(color='#94a3b8', size=9))
    fig.update_layout(
        margin=dict(l=10, r=60, t=10, b=10),
        xaxis=dict(visible=True, title='Relative Risk',
                   tickfont=dict(color='#94a3b8', size=10)),
        yaxis=dict(tickfont=dict(family='Inter', size=10, color='#475569'), automargin=True),
        height=380, showlegend=False,
    )
    return fig


@callback(
    Output('tr-scatter', 'figure'),
    Input('tr-year-slider', 'value'),
    Input('tr-scatter-x', 'value'),
)
def update_scatter(year_range, x_col):
    tahun = int(year_range[1])
    df_y  = DF[DF['Tahun'] == tahun].copy()

    if df_y.empty or x_col not in df_y.columns or df_y[x_col].isna().all():
        fig = go.Figure()
        fig.add_annotation(text='Data tidak tersedia', x=0.5, y=0.5,
                           xref='paper', yref='paper', showarrow=False,
                           font=dict(size=14, color='#94a3b8'))
        apply_chart_styling(fig)
        return fig

    x_label = next((o['label'] for o in KOVARIAT_OPTIONS if o['value'] == x_col), x_col)

    df_y = df_y.dropna(subset=[x_col, 'RR'])
    rr_min, rr_max = df_y['RR'].min(), df_y['RR'].max()

    # Color by RR intensity (orange gradient)
    colors = []
    for rr in df_y['RR']:
        ratio = (rr - rr_min) / (rr_max - rr_min + 1e-9)
        if ratio > 0.66:
            colors.append('#FF0000')
        elif ratio > 0.33:
            colors.append('#FF5500')
        else:
            colors.append('#FFC800')

    # Size by PHK
    size_vals = df_y['PHK'].fillna(50)
    size_norm = 8 + (size_vals - size_vals.min()) / (size_vals.max() - size_vals.min() + 1e-9) * 22

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_y[x_col],
        y=df_y['RR'],
        mode='markers+text',
        marker=dict(
            size=size_norm,
            color=colors,
            line=dict(color='white', width=1),
            opacity=0.85,
        ),
        text=df_y['Provinsi'],
        textposition='top center',
        textfont=dict(family='Inter', size=8, color='#64748b'),
        hovertemplate=(
            '<b>%{text}</b><br>'
            + x_label + ': %{x:.2f}<br>'
            'RR: %{y:.3f}<br>'
            'PHK: %{customdata:,}'
            '<extra></extra>'
        ),
        customdata=df_y['PHK'].astype(int),
        showlegend=False,
    ))

    x_vals = df_y[x_col].values
    y_vals = df_y['RR'].values
    if len(x_vals) > 2:
        coeffs = np.polyfit(x_vals, y_vals, 1)
        x_line = np.linspace(x_vals.min(), x_vals.max(), 50)
        y_line = np.polyval(coeffs, x_line)
        fig.add_trace(go.Scatter(
            x=x_line, y=y_line,
            mode='lines',
            line=dict(color='rgba(255,85,0,0.4)', width=2, dash='dash'),
            name='Tren linear',
            hoverinfo='skip',
        ))
        corr = np.corrcoef(x_vals, y_vals)[0, 1]
        fig.add_annotation(
            text=f'r = {corr:.3f}',
            x=0.02, y=0.98, xref='paper', yref='paper',
            showarrow=False, bgcolor='rgba(255,255,255,0.85)',
            bordercolor='#d1dce6', borderwidth=1, borderpad=6,
            font=dict(family='Inter', size=12, color='#FF5500'),
        )

    fig.add_hline(y=1.0, line_dash='dot', line_color='#94a3b8',
                  annotation_text='RR = 1',
                  annotation_font=dict(color='#94a3b8', size=9))

    apply_chart_styling(fig)
    fig.update_layout(
        margin=dict(l=50, r=20, t=20, b=50),
        xaxis_title=x_label,
        yaxis_title='Relative Risk (RR)',
        height=380,
        showlegend=False,
    )
    return fig


@callback(Output('tr-fixed-effects', 'figure'), Input('tr-year-slider', 'value'))
def update_fixed_effects(_year_range):
    """Forest plot fixed effects dengan 95% CI."""
    try:
        df_fe = FIXED_FX.copy()
        var_col  = 'Variabel' if 'Variabel' in df_fe.columns else df_fe.columns[0]
        mean_col = 'Mean'     if 'Mean'     in df_fe.columns else df_fe.columns[1]
        lo_col   = '2.5%'     if '2.5%'     in df_fe.columns else df_fe.columns[2]
        hi_col   = '97.5%'    if '97.5%'    in df_fe.columns else df_fe.columns[3]

        df_plot = df_fe[df_fe[var_col] != '(Intercept)'].copy()

        fig = go.Figure()
        for _, row in df_plot.iterrows():
            mean_v = float(row[mean_col])
            lo_v   = float(row[lo_col])
            hi_v   = float(row[hi_col])
            var    = str(row[var_col])

            color = '#FF0000' if lo_v > 0 else '#16a34a' if hi_v < 0 else '#FF8F00'

            fig.add_trace(go.Scatter(
                x=[lo_v, hi_v], y=[var, var],
                mode='lines', line=dict(color=color, width=3),
                showlegend=False, hoverinfo='skip',
            ))
            fig.add_trace(go.Scatter(
                x=[mean_v], y=[var],
                mode='markers',
                marker=dict(size=10, color=color, line=dict(color='white', width=1.5)),
                showlegend=False,
                hovertemplate=f'<b>{var}</b><br>β = {mean_v:.4f}<br>95% CI: ({lo_v:.4f}, {hi_v:.4f})<extra></extra>',
            ))

        fig.add_vline(x=0, line_dash='dot', line_color='#94a3b8',
                      annotation_text='β=0', annotation_font=dict(color='#94a3b8', size=9))
        apply_chart_styling(fig, '')
        fig.update_layout(
            margin=dict(l=10, r=20, t=10, b=40),
            xaxis=dict(title='Koefisien (β)', zeroline=True),
            yaxis=dict(automargin=True, tickfont=dict(size=11)),
            height=280, showlegend=False,
        )
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f'Error: {e}', x=0.5, y=0.5, showarrow=False)
        return fig


@callback(
    Output('tr-data-table', 'children'),
    Input('tr-year-slider', 'value'),
    Input('tr-prov-dropdown', 'value'),
)
def update_table(year_range, sel_provs):
    tahun = year_range[1]
    df_y  = DF[DF['Tahun'] == tahun].copy()
    if sel_provs:
        df_y = df_y[df_y['Provinsi'].isin(sel_provs)]
    df_y = df_y.sort_values('RR', ascending=False)

    cols = [
        {'name': 'Provinsi', 'id': 'Provinsi'},
        {'name': 'RR', 'id': 'RR', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=4, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'PHK', 'id': 'PHK', 'type': 'numeric',
         'format': dash_table.Format.Format(group=True)},
    ]
    if 'TPAK' in df_y.columns and df_y['TPAK'].notna().any():
        cols.append({'name': 'TPAK (%)', 'id': 'TPAK', 'type': 'numeric',
                     'format': dash_table.Format.Format(precision=1, scheme=dash_table.Format.Scheme.fixed)})
    if 'IPM' in df_y.columns and df_y['IPM'].notna().any():
        cols.append({'name': 'IPM', 'id': 'IPM', 'type': 'numeric',
                     'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)})

    table = dash_table.DataTable(
        id='tr-detail-table',
        columns=cols,
        data=df_y.to_dict('records'),
        sort_action='native', filter_action='native',
        page_size=10, export_format='csv',
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': '#fff3e0', 'fontFamily': 'Inter',
            'fontWeight': '600', 'color': '#FF5500',
            'border': 'none', 'borderBottom': '1px solid #d1dce6',
            'padding': '12px 16px', 'textAlign': 'left',
        },
        style_cell={
            'backgroundColor': '#ffffff', 'fontFamily': 'Inter',
            'fontSize': '13px', 'color': '#475569',
            'border': 'none', 'borderBottom': '1px solid #e8eff4',
            'padding': '10px 16px', 'textAlign': 'left',
            'minWidth': '100px',
        },
        style_data_conditional=[
            {'if': {'filter_query': '{RR} > 1.5', 'column_id': 'RR'},
             'backgroundColor': 'rgba(255,0,0,0.10)', 'color': '#FF0000', 'fontWeight': '600'},
            {'if': {'filter_query': '{RR} > 1.0 && {RR} <= 1.5', 'column_id': 'RR'},
             'backgroundColor': 'rgba(255,85,0,0.10)', 'color': '#FF5500', 'fontWeight': '600'},
            {'if': {'filter_query': '{RR} < 1.0', 'column_id': 'RR'},
             'backgroundColor': 'rgba(22,163,74,0.08)', 'color': '#16a34a', 'fontWeight': '600'},
            {'if': {'state': 'active'},
             'backgroundColor': 'rgba(255,85,0,0.06)', 'border': 'none'},
        ],
        style_as_list_view=True,
    )
    return table
