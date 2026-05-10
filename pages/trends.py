"""
Page 2: Tren & Analisis TBC
Tren RR temporal, ranking provinsi, scatter kovariat vs RR, fixed effects table.
"""
from dash import html, dcc, callback, Input, Output, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from data.tbc_data_loader import (
    load_tbc_data, load_fixed_effects, load_temporal,
    COLORS, get_national_agg
)
from components.chart_utils import apply_chart_styling

# ── Load data ───────────────────────────────────────────────────────────────
DF       = load_tbc_data()
AGG      = get_national_agg(DF)
FIXED_FX = load_fixed_effects()
TEMPORAL = load_temporal()
PROVINSI_LIST = sorted(DF['Provinsi'].unique().tolist())
YEARS         = sorted(DF['Tahun'].unique().tolist())

KOVARIAT_OPTIONS = [
    {'label': 'Sanitasi Layak (%)',        'value': 'Sanitasi'},
    {'label': 'Air Minum Layak (%)',        'value': 'AirMinum'},
    {'label': 'Rata-rata Lama Sekolah',     'value': 'LamaSekolah'},
    {'label': 'Rumah Layak (%)',            'value': 'RumahLayak'},
    {'label': 'Kemiskinan (%)',             'value': 'Kemiskinan'},
    {'label': 'Kepadatan Penduduk',         'value': 'Kepadatan'},
]


def layout():
    return html.Div([
        # ── Header ──
        html.Div([
            html.Div([
                html.H2('Tren & Analisis TBC', className='page-title gradient-text'),
                html.P('Perkembangan temporal, korelasi kovariat, dan hasil model INLA CAR Leroux',
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
                        {'label': 'Rate/100k', 'value': 'Rate_per100k'},
                    ],
                    value='RR', inline=True,
                    className='btn-group',
                    inputClassName='btn-check',
                    labelClassName='btn btn-outline-secondary btn-sm',
                    labelCheckedClassName='active',
                ),
            ], style={'flex': '1', 'minWidth': '160px'}),
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
                            value='Sanitasi', clearable=False,
                            className='dash-dropdown',
                            style={'width': '200px', 'marginLeft': 'auto'},
                        ),
                    ], style={'display': 'flex', 'justifyContent': 'space-between',
                              'alignItems': 'center', 'flexWrap': 'wrap', 'gap': '8px',
                              'marginBottom': '12px'}),
                    dcc.Graph(id='tr-scatter', config={'displayModeBar': True},
                              style={'height': '400px'}),
                ], className='glass-card'),
            ], lg=7, md=12),
        ], className='g-3 section-gap'),

        # ── Efek Temporal + Fixed Effects ──
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div('Efek Random Temporal (RW1)', className='chart-title'),
                    dcc.Graph(id='tr-temporal-chart', config={'displayModeBar': False},
                              style={'height': '320px'}),
                ], className='glass-card'),
            ], lg=6, md=12),

            dbc.Col([
                html.Div([
                    html.Div('Estimasi Fixed Effects (Kovariat)', className='chart-title'),
                    dcc.Graph(id='tr-fixed-effects', config={'displayModeBar': False},
                              style={'height': '320px'}),
                ], className='glass-card'),
            ], lg=6, md=12),
        ], className='g-3 section-gap fade-in-up'),

        # ── Data Table ──
        html.Div([
            html.Div([
                html.Span('📋 Data Detail per Provinsi', className='chart-title'),
                html.Span(' — Klik header untuk sort',
                          style={'fontSize': '11px', 'color': '#64748b', 'marginLeft': '8px'}),
            ], style={'marginBottom': '16px'}),
            html.Div(id='tr-data-table'),
        ], className='glass-card section-gap fade-in-up'),

        # ── Footer ──
        html.Div([
            '🫁 Dashboard TBC Indonesia | Model: Bayesian CAR Leroux Spasio-Temporal (INLA)',
            html.Br(),
            '📊 Sumber Data: BPS, Kemenkes RI | Periode: 2020–2025',
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
    agg = AGG[(AGG['Tahun'] >= y0) & (AGG['Tahun'] <= y1)]
    metric_col = 'rata_rr' if metric == 'RR' else 'rata_rate'
    label = 'Rata-rata RR Nasional' if metric == 'RR' else 'Angka Penemuan /100k Nasional'
    title = f'Tren {label} ({y0}–{y1})'
    y_label = 'Relative Risk (RR)' if metric == 'RR' else 'Per 100.000 Penduduk'

    fig = go.Figure()

    # National line
    show_dashed = bool(sel_provs)
    fig.add_trace(go.Scatter(
        x=agg['Tahun'], y=agg[metric_col],
        name='Nasional', mode='lines+markers',
        line=dict(color='#3d8b8a', width=3,
                  dash='dash' if show_dashed else 'solid'),
        marker=dict(size=7),
        fill='tozeroy' if not show_dashed else None,
        fillcolor='rgba(61,139,138,0.10)' if not show_dashed else None,
    ))

    # Reference line RR=1
    if metric == 'RR':
        fig.add_hline(y=1.0, line_dash='dot', line_color='#c0775a',
                      annotation_text='RR = 1 (Rata-rata Nasional)',
                      annotation_position='bottom right',
                      annotation_font=dict(color='#c0775a', size=10, family='Inter'))

    # Province lines
    if sel_provs:
        colors = COLORS['chart_sequence']
        col_map = {'RR': 'RR', 'Rate_per100k': 'Rate_per100k'}
        for i, prov in enumerate(sel_provs[:5]):
            df_p = DF[(DF['Provinsi'] == prov) &
                      (DF['Tahun'] >= y0) & (DF['Tahun'] <= y1)]
            fig.add_trace(go.Scatter(
                x=df_p['Tahun'], y=df_p[col_map[metric]],
                name=prov, mode='lines+markers',
                line=dict(color=colors[i % len(colors)], width=2),
                marker=dict(size=5),
            ))

    apply_chart_styling(fig, '')
    fig.update_layout(
        hovermode='x unified',
        xaxis=dict(dtick=1, rangeslider=dict(visible=True, thickness=0.05)),
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
        df_p = df_y.nlargest(10, 'RR').sort_values('RR')
        colors = ['#b8d4e3','#9fc5d5','#7caec4','#6aa1b5','#5ba4a4',
                  '#4a9498','#3d8b8a','#d97f7f','#d94f4f','#c0302e']
    else:
        df_p = df_y.nsmallest(10, 'RR').sort_values('RR', ascending=False)
        colors = ['#e0f2f1','#b2dfdb','#80cbc4','#4db6ac','#26a69a',
                  '#1a8c82','#147a70','#0e685f','#085650','#044440']

    n = len(df_p)
    color_list = [colors[int(i*(len(colors)-1)/max(n-1,1))] for i in range(n)]

    fig = go.Figure(go.Bar(
        x=df_p['RR'], y=df_p['Provinsi'], orientation='h',
        marker=dict(color=color_list),
        text=df_p['RR'].apply(lambda x: f'{x:.3f}'),
        textposition='outside',
        textfont=dict(family='Inter', size=11, color='#475569'),
        hovertemplate='<b>%{y}</b><br>RR: %{x:.3f}<extra></extra>',
    ))
    apply_chart_styling(fig)
    fig.add_vline(x=1.0, line_dash='dot', line_color='#c0775a',
                  annotation_text='RR=1', annotation_font=dict(color='#c0775a', size=9))
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
    tahun = year_range[1]
    df_y  = DF[DF['Tahun'] == tahun].copy()
    x_label = next((o['label'] for o in KOVARIAT_OPTIONS if o['value'] == x_col), x_col)

    fig = px.scatter(
        df_y, x=x_col, y='RR',
        hover_name='Provinsi',
        color='RR',
        color_continuous_scale=[[0,'#2e8b57'],[0.5,'#4a8fa8'],[1,'#d94f4f']],
        size='Rate_per100k', size_max=30,
        trendline='ols',
        labels={x_col: x_label, 'RR': 'Relative Risk (RR)',
                'Rate_per100k': 'Angka Penemuan /100k'},
    )
    # Style trendline
    for trace in fig.data:
        if hasattr(trace, 'mode') and trace.mode == 'lines':
            trace.line = dict(color='rgba(61,139,138,0.4)', width=1.5, dash='dash')

    # Annotate top 3 outliers by RR
    if len(df_y) > 3:
        outliers = df_y.nlargest(3, 'RR')
        for _, row in outliers.iterrows():
            fig.add_annotation(
                x=row[x_col], y=row['RR'], text=row['Provinsi'],
                showarrow=True, arrowhead=0,
                font=dict(family='Inter', size=9, color='#475569'),
                arrowcolor='#94a3b8', ax=20, ay=-25,
                bgcolor='rgba(255,255,255,0.9)', borderpad=3,
            )

    fig.add_hline(y=1.0, line_dash='dot', line_color='#c0775a',
                  annotation_text='RR=1', annotation_font=dict(color='#c0775a', size=9))
    apply_chart_styling(fig)
    fig.update_layout(
        margin=dict(l=50, r=20, t=20, b=50),
        coloraxis_showscale=False, height=380,
        xaxis_title=x_label, yaxis_title='Relative Risk (RR)',
    )
    return fig


@callback(Output('tr-temporal-chart', 'figure'), Input('tr-year-slider', 'value'))
def update_temporal(_year_range):
    """Plot efek random temporal RW1."""
    try:
        df_t = TEMPORAL.copy()
        # Kolom: ID, Tahun, mean, sd, 0.025quant, 0.975quant, mode
        x_col    = 'Tahun' if 'Tahun' in df_t.columns else 'ID'
        mean_col = 'mean'
        lo_col   = '0.025quant'
        hi_col   = '0.975quant'

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_t[x_col], y=df_t[hi_col],
            mode='lines', line=dict(width=0),
            showlegend=False, hoverinfo='skip',
        ))
        fig.add_trace(go.Scatter(
            x=df_t[x_col], y=df_t[lo_col],
            fill='tonexty', fillcolor='rgba(61,139,138,0.15)',
            mode='lines', line=dict(width=0),
            name='95% CI', hoverinfo='skip',
        ))
        fig.add_trace(go.Scatter(
            x=df_t[x_col], y=df_t[mean_col],
            mode='lines+markers',
            line=dict(color='#3d8b8a', width=2.5),
            marker=dict(size=7, color='#3d8b8a'),
            name='Mean posterior',
            hovertemplate='Tahun %{x}<br>Efek: %{y:.4f}<extra></extra>',
        ))
        fig.add_hline(y=0, line_dash='dot', line_color='#94a3b8')
        apply_chart_styling(fig, '')
        fig.update_layout(
            margin=dict(l=50, r=20, t=10, b=40),
            xaxis=dict(dtick=1, title='Tahun'),
            yaxis=dict(title='Efek Random'),
            height=290, showlegend=True,
            legend=dict(y=-0.25, x=0.5, xanchor='center', orientation='h'),
        )
        return fig
    except Exception as e:
        fig = go.Figure()
        fig.add_annotation(text=f'Error: {e}', x=0.5, y=0.5, showarrow=False)
        return fig


@callback(Output('tr-fixed-effects', 'figure'), Input('tr-year-slider', 'value'))
def update_fixed_effects(_year_range):
    """Forest plot fixed effects dengan 95% CI."""
    try:
        df_fe = FIXED_FX.copy()
        # Filter out intercept for cleaner display
        if 'Variabel' in df_fe.columns:
            var_col = 'Variabel'
        else:
            var_col = df_fe.columns[0]

        df_plot = df_fe[df_fe[var_col] != 'Intercept'].copy()

        mean_col = 'mean'
        lo_col   = '0.025quant'
        hi_col   = '0.975quant'

        fig = go.Figure()
        colors = ['#d94f4f' if float(row[lo_col]) > 0
                  else '#2e8b57' if float(row[hi_col]) < 0
                  else '#94a3b8'
                  for _, row in df_plot.iterrows()]

        for i, (_, row) in enumerate(df_plot.iterrows()):
            mean_v = float(row[mean_col])
            lo_v   = float(row[lo_col])
            hi_v   = float(row[hi_col])
            var    = str(row[var_col])

            fig.add_trace(go.Scatter(
                x=[lo_v, hi_v], y=[var, var],
                mode='lines', line=dict(color=colors[i], width=3),
                showlegend=False, hoverinfo='skip',
            ))
            fig.add_trace(go.Scatter(
                x=[mean_v], y=[var],
                mode='markers',
                marker=dict(size=10, color=colors[i],
                            line=dict(color='white', width=1.5)),
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
            height=290, showlegend=False,
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
        {'name': 'Provinsi',          'id': 'Provinsi'},
        {'name': 'RR',                'id': 'RR', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=4, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Angka Penemuan/100k','id': 'Rate_per100k', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=1, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Sanitasi (%)',       'id': 'Sanitasi', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=1, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Air Minum (%)',      'id': 'AirMinum', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=1, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Lama Sekolah',       'id': 'LamaSekolah', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Rumah Layak (%)',    'id': 'RumahLayak', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=1, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Kemiskinan (%)',     'id': 'Kemiskinan', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
    ]

    table = dash_table.DataTable(
        id='tr-detail-table',
        columns=cols,
        data=df_y.to_dict('records'),
        sort_action='native', filter_action='native',
        page_size=10, export_format='csv',
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': '#e0f2f1', 'fontFamily': 'Inter',
            'fontWeight': '600', 'color': '#2a7c8c',
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
             'backgroundColor': 'rgba(217,79,79,0.15)', 'color': '#d94f4f', 'fontWeight': '600'},
            {'if': {'filter_query': '{RR} > 1.0 && {RR} <= 1.5', 'column_id': 'RR'},
             'backgroundColor': 'rgba(192,119,90,0.15)', 'color': '#c0775a', 'fontWeight': '600'},
            {'if': {'filter_query': '{RR} < 1.0', 'column_id': 'RR'},
             'backgroundColor': 'rgba(46,139,87,0.12)', 'color': '#2e8b57', 'fontWeight': '600'},
            {'if': {'state': 'active'},
             'backgroundColor': 'rgba(42,124,140,0.08)', 'border': 'none'},
        ],
        style_as_list_view=True,
    )
    return table
