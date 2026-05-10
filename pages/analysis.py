"""
Page 3: Analisis & Korelasi
Scatter plot, Donut chart, Data Table.
"""
from dash import html, dcc, callback, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from data.dummy_data import generate_data, COLORS
from components.chart_utils import apply_chart_styling

# ── Load data ──
DF = generate_data()
PROVINSI_LIST = sorted(DF['provinsi'].unique().tolist())
PULAU_LIST = sorted(DF['pulau'].unique().tolist())

INDIKATOR_OPTIONS = [
    {'label': 'IPM', 'value': 'ipm'},
    {'label': 'Pengangguran (%)', 'value': 'pengangguran'},
    {'label': 'Rata-rata Lama Sekolah', 'value': 'rata_lama_sekolah'},
    {'label': 'Pengeluaran per Kapita', 'value': 'pengeluaran_perkapita'},
    {'label': 'Gini Ratio', 'value': 'gini_ratio'},
    {'label': 'Persentase Kemiskinan (%)', 'value': 'persentase_kemiskinan'},
    {'label': 'Indeks Kedalaman P1', 'value': 'indeks_kedalaman_p1'},
    {'label': 'Indeks Keparahan P2', 'value': 'indeks_keparahan_p2'},
]

INDIKATOR_LABELS = {opt['value']: opt['label'] for opt in INDIKATOR_OPTIONS}


def layout():
    """Return Analysis & Correlation page layout."""
    return html.Div([
        # ── Header ──
        html.Div([
            html.Div([
                html.H2('Analisis & Korelasi', className='page-title gradient-text'),
                html.P('Eksplorasi hubungan antar indikator kemiskinan dan pembangunan',
                       className='page-subtitle'),
            ]),
        ], className='page-header'),
        
        # ── Filter Bar ──
        html.Div([
            html.Div([
                html.Label('Tahun:', style={
                    'fontSize': '11px', 'color': '#94a3b8', 'fontFamily': 'Inter',
                    'textTransform': 'uppercase', 'letterSpacing': '2px', 'marginBottom': '4px',
                }),
                dcc.Dropdown(
                    id='analysis-year',
                    options=[{'label': str(y), 'value': y} for y in range(2024, 2017, -1)],
                    value=2024, clearable=False, className='dash-dropdown',
                ),
            ], style={'minWidth': '100px'}),
            
            html.Div([
                html.Label('Indikator X:', style={
                    'fontSize': '11px', 'color': '#94a3b8', 'fontFamily': 'Inter',
                    'textTransform': 'uppercase', 'letterSpacing': '2px', 'marginBottom': '4px',
                }),
                dcc.Dropdown(
                    id='analysis-x-axis',
                    options=INDIKATOR_OPTIONS,
                    value='ipm', clearable=False, className='dash-dropdown',
                ),
            ], style={'minWidth': '180px', 'flex': '1'}),
            
            html.Div([
                html.Label('Indikator Y:', style={
                    'fontSize': '11px', 'color': '#94a3b8', 'fontFamily': 'Inter',
                    'textTransform': 'uppercase', 'letterSpacing': '2px', 'marginBottom': '4px',
                }),
                dcc.Dropdown(
                    id='analysis-y-axis',
                    options=INDIKATOR_OPTIONS,
                    value='persentase_kemiskinan', clearable=False, className='dash-dropdown',
                ),
            ], style={'minWidth': '180px', 'flex': '1'}),
            
            html.Div([
                html.Label('Filter Pulau:', style={
                    'fontSize': '11px', 'color': '#94a3b8', 'fontFamily': 'Inter',
                    'textTransform': 'uppercase', 'letterSpacing': '2px', 'marginBottom': '4px',
                }),
                dcc.Dropdown(
                    id='analysis-pulau-filter',
                    options=[{'label': p, 'value': p} for p in PULAU_LIST],
                    value=[], multi=True,
                    placeholder='Semua pulau...',
                    className='dash-dropdown',
                ),
            ], style={'minWidth': '200px', 'flex': '1'}),
        ], className='glass-card', style={
            'display': 'flex', 'gap': '16px', 'alignItems': 'flex-end',
            'flexWrap': 'wrap', 'padding': '20px 24px', 'marginBottom': '24px',
        }),
        
        # ── Scatter + Donut Row ──
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Div('Scatter Plot Korelasi', className='chart-title'),
                    dcc.Graph(id='scatter-plot', config={'displayModeBar': True},
                              style={'height': '450px'}),
                ], className='glass-card'),
            ], lg=7, md=12),
            
            dbc.Col([
                html.Div([
                    html.Div('Distribusi Penduduk Miskin per Pulau', className='chart-title'),
                    dcc.Graph(id='donut-chart', config={'displayModeBar': False},
                              style={'height': '450px'}),
                ], className='glass-card'),
            ], lg=5, md=12),
        ], className='g-3 fade-in-up'),
        
        # ── Data Table ──
        html.Div([
            html.Div([
                html.Span('📋 Data Detail', className='chart-title'),
                html.Span(' — Klik header untuk sort, gunakan filter di bawah header',
                          style={'fontSize': '11px', 'color': '#64748b', 'marginLeft': '8px'}),
            ], style={'marginBottom': '16px'}),
            
            html.Div(id='data-table-container'),
        ], className='glass-card section-gap fade-in-up'),
        
        # ── Footer ──
        html.Div([
            '📊 Sumber Data: Badan Pusat Statistik (bps.go.id) | Data Dummy untuk Demonstrasi',
            html.Br(),
            'Terakhir diperbarui: Maret 2024 | Dibuat dengan Plotly Dash',
        ], className='dashboard-footer'),
        
    ], className='page-content')


# ═══════════════════════════════════════════════════════════════════════
# CALLBACKS
# ═══════════════════════════════════════════════════════════════════════

@callback(
    Output('scatter-plot', 'figure'),
    Input('analysis-year', 'value'),
    Input('analysis-x-axis', 'value'),
    Input('analysis-y-axis', 'value'),
    Input('analysis-pulau-filter', 'value'),
)
def update_scatter(tahun, x_col, y_col, pulau_filter):
    """Update scatter plot."""
    df_year = DF[DF['tahun'] == tahun].copy()
    
    if pulau_filter:
        df_year = df_year[df_year['pulau'].isin(pulau_filter)]
    
    if df_year.empty:
        return go.Figure()
    
    fig = px.scatter(
        df_year,
        x=x_col,
        y=y_col,
        size='jumlah_penduduk_miskin',
        color='pulau',
        hover_name='provinsi',
        hover_data={
            x_col: ':.2f',
            y_col: ':.2f',
            'jumlah_penduduk_miskin': ':,',
            'pulau': True,
        },
        color_discrete_sequence=COLORS['chart_sequence'],
        trendline='ols',
        labels={
            x_col: INDIKATOR_LABELS.get(x_col, x_col),
            y_col: INDIKATOR_LABELS.get(y_col, y_col),
            'jumlah_penduduk_miskin': 'Penduduk Miskin',
        },
        size_max=40,
    )
    
    # Style trendline
    for trace in fig.data:
        if trace.mode == 'lines':
            trace.line = dict(color='rgba(61,139,138,0.35)', width=1.5, dash='dash')
    
    # Add outlier annotations (top 3 furthest from mean)
    if len(df_year) > 3:
        y_mean = df_year[y_col].mean()
        df_year['deviation'] = abs(df_year[y_col] - y_mean)
        outliers = df_year.nlargest(3, 'deviation')
        for _, row in outliers.iterrows():
            fig.add_annotation(
                x=row[x_col], y=row[y_col],
                text=row['provinsi'],
                showarrow=True, arrowhead=0,
                font=dict(family='Inter', size=9, color='#475569'),
                arrowcolor='#94a3b8',
                ax=20, ay=-20,
                bgcolor='rgba(255,255,255,0.9)',
                borderpad=3,
            )
    
    apply_chart_styling(fig)
    fig.update_layout(
        xaxis_title=INDIKATOR_LABELS.get(x_col, x_col),
        yaxis_title=INDIKATOR_LABELS.get(y_col, y_col),
        margin=dict(l=50, r=20, t=20, b=50),
        legend=dict(y=-0.2),
        dragmode='select',
    )
    
    return fig


@callback(
    Output('donut-chart', 'figure'),
    Input('analysis-year', 'value'),
    Input('analysis-pulau-filter', 'value'),
    Input('scatter-plot', 'selectedData'),
)
def update_donut(tahun, pulau_filter, selected_data):
    """Update donut chart."""
    df_year = DF[DF['tahun'] == tahun].copy()
    
    if pulau_filter:
        df_year = df_year[df_year['pulau'].isin(pulau_filter)]
    
    # If scatter brush selection, filter
    if selected_data and 'points' in selected_data:
        selected_provs = [p.get('hovertext', '') for p in selected_data['points']
                          if p.get('hovertext')]
        if selected_provs:
            df_year = df_year[df_year['provinsi'].isin(selected_provs)]
    
    # Aggregate by island
    agg = df_year.groupby('pulau')['jumlah_penduduk_miskin'].sum().reset_index()
    agg = agg.sort_values('jumlah_penduduk_miskin', ascending=False)
    
    total = agg['jumlah_penduduk_miskin'].sum()
    total_juta = total / 1_000_000
    
    # Pull largest segment
    pull_values = [0.05 if i == 0 else 0 for i in range(len(agg))]
    
    fig = go.Figure(go.Pie(
        labels=agg['pulau'],
        values=agg['jumlah_penduduk_miskin'],
        hole=0.65,
        marker=dict(
            colors=COLORS['chart_sequence'][:len(agg)],
            line=dict(color='#ffffff', width=2),
        ),
        textinfo='label+percent',
        textfont=dict(family='Inter', size=11, color='#475569'),
        hovertemplate='<b>%{label}</b><br>Penduduk Miskin: %{value:,}<br>Kontribusi: %{percent}<extra></extra>',
        pull=pull_values,
    ))
    
    # Center text
    fig.add_annotation(
        text=f'<b>{total_juta:.1f} Jt</b><br><span style="font-size:10px;color:#64748b">Total</span>',
        x=0.5, y=0.5, showarrow=False,
        font=dict(family='Outfit', size=22, color='#1e293b'),
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter', color='#475569'),
        showlegend=True,
        legend=dict(
            orientation='h', yanchor='bottom', y=-0.15,
            xanchor='center', x=0.5,
            font=dict(color='#475569', size=10),
            bgcolor='rgba(0,0,0,0)',
        ),
        margin=dict(l=20, r=20, t=20, b=40),
        transition_duration=800,
        hoverlabel=dict(
            bgcolor='#ffffff',
            bordercolor='#d1dce6',
            font=dict(family='Inter', size=12, color='#1e293b'),
        ),
    )
    
    return fig


@callback(
    Output('data-table-container', 'children'),
    Input('analysis-year', 'value'),
    Input('analysis-pulau-filter', 'value'),
    Input('scatter-plot', 'selectedData'),
    Input('donut-chart', 'clickData'),
)
def update_data_table(tahun, pulau_filter, selected_data, donut_click):
    """Update the data table."""
    df_year = DF[DF['tahun'] == tahun].copy()
    
    if pulau_filter:
        df_year = df_year[df_year['pulau'].isin(pulau_filter)]
    
    # Filter by scatter selection
    if selected_data and 'points' in selected_data:
        selected_provs = [p.get('hovertext', '') for p in selected_data['points']
                          if p.get('hovertext')]
        if selected_provs:
            df_year = df_year[df_year['provinsi'].isin(selected_provs)]
    
    # Filter by donut click
    if donut_click and 'points' in donut_click:
        try:
            clicked_pulau = donut_click['points'][0].get('label')
            if clicked_pulau:
                df_year = df_year[df_year['pulau'] == clicked_pulau]
        except (IndexError, KeyError):
            pass
    
    # Select and format columns
    columns_display = [
        {'name': 'Provinsi', 'id': 'provinsi'},
        {'name': 'Pulau', 'id': 'pulau'},
        {'name': 'Penduduk Miskin', 'id': 'jumlah_penduduk_miskin', 'type': 'numeric',
         'format': dash_table.Format.Format(group=True)},
        {'name': 'Kemiskinan (%)', 'id': 'persentase_kemiskinan', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Gini Ratio', 'id': 'gini_ratio', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=3, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'IPM', 'id': 'ipm', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Pengangguran (%)', 'id': 'pengangguran', 'type': 'numeric',
         'format': dash_table.Format.Format(precision=2, scheme=dash_table.Format.Scheme.fixed)},
        {'name': 'Pengeluaran/Kapita', 'id': 'pengeluaran_perkapita', 'type': 'numeric',
         'format': dash_table.Format.Format(group=True)},
        {'name': 'Penerima Bansos', 'id': 'penerima_bansos', 'type': 'numeric',
         'format': dash_table.Format.Format(group=True)},
    ]
    
    table = dash_table.DataTable(
        id='analysis-data-table',
        columns=columns_display,
        data=df_year.to_dict('records'),
        sort_action='native',
        filter_action='native',
        page_size=10,
        export_format='csv',
        export_headers='display',
        
        style_table={
            'overflowX': 'auto',
            'minWidth': '100%',
        },
        style_header={
            'backgroundColor': '#e0f2f1',
            'fontFamily': 'Inter',
            'fontWeight': '600',
            'color': '#2a7c8c',
            'border': 'none',
            'borderBottom': '1px solid #d1dce6',
            'padding': '12px 16px',
            'textAlign': 'left',
        },
        style_cell={
            'backgroundColor': '#ffffff',
            'fontFamily': 'Inter',
            'fontSize': '13px',
            'color': '#475569',
            'border': 'none',
            'borderBottom': '1px solid #e8eff4',
            'padding': '10px 16px',
            'textAlign': 'left',
            'minWidth': '100px',
            'maxWidth': '200px',
        },
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
        },
        style_filter={
            'backgroundColor': '#f8fafc',
            'fontFamily': 'Inter',
            'fontSize': '12px',
            'color': '#1e293b',
            'border': '1px solid #d1dce6',
        },
        style_data_conditional=[
            # High poverty (>15%) - red highlight
            {
                'if': {
                    'filter_query': '{persentase_kemiskinan} > 15',
                    'column_id': 'persentase_kemiskinan',
                },
                'backgroundColor': 'rgba(239, 68, 68, 0.15)',
                'color': '#ef4444',
                'fontWeight': '600',
            },
            # Low poverty (<7%) - green highlight
            {
                'if': {
                    'filter_query': '{persentase_kemiskinan} < 7',
                    'column_id': 'persentase_kemiskinan',
                },
                'backgroundColor': 'rgba(34, 197, 94, 0.15)',
                'color': '#22c55e',
                'fontWeight': '600',
            },
            # Low IPM (<65) - yellow highlight
            {
                'if': {
                    'filter_query': '{ipm} < 65',
                    'column_id': 'ipm',
                },
                'backgroundColor': 'rgba(245, 158, 11, 0.15)',
                'color': '#f59e0b',
                'fontWeight': '600',
            },
            # Hover effect  
            {
                'if': {'state': 'active'},
                'backgroundColor': 'rgba(42,124,140,0.08)',
                'border': 'none',
            },
        ],
        style_as_list_view=True,
    )
    
    return table
