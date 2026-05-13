"""
Sidebar Component — Dashboard PHK Indonesia
Orange sidebar dengan navigasi dan sliding active indicator.
"""
from dash import html
import dash_bootstrap_components as dbc


def create_sidebar():
    """Create the sidebar navigation with sliding tab indicator."""
    return html.Div([
        # ── Logo / Title ──
        html.Div([
            html.Img(src='/assets/Lawan TBC.png', style={
                'width': '170px', 'height': 'auto', 'marginBottom': '8px',
                'borderRadius': '12px',
            }),
            html.Div('PHK INDONESIA', className='sidebar-logo-text'),
            html.Div('Dashboard Analitik Spasial', className='sidebar-logo-sub'),
        ], className='sidebar-logo'),

        # ── Navigation ──
        html.Div([
            html.Hr(className='sidebar-divider'),

            # Sliding active indicator
            html.Div(id='nav-indicator', className='nav-indicator'),

            dbc.NavLink([
                html.Span('📌', className='sidebar-link-icon'),
                html.Span('Overview PHK'),
            ], href='/', id='nav-overview', className='sidebar-link'),

            dbc.NavLink([
                html.Span('📈', className='sidebar-link-icon'),
                html.Span('Tren & Analisis'),
            ], href='/trends', id='nav-trends', className='sidebar-link'),

        ], className='sidebar-nav', style={'position': 'relative'}),

        # ── Bottom Actions ──
        html.Div([
            html.Button([
                html.Span('▶', className='sidebar-link-icon'),
                html.Span('Mulai Tour'),
            ], id='btn-start-tour', className='sidebar-link', n_clicks=0),

            html.Button([
                html.Span('ℹ', className='sidebar-link-icon'),
                html.Span('Tentang'),
            ], id='btn-about', className='sidebar-link', n_clicks=0),

            html.Hr(className='sidebar-divider'),

            html.Div([
                html.Div('Model: Bayesian ST-CAR', style={
                    'fontSize': '10px', 'color': 'rgba(255,255,255,0.5)',
                    'textAlign': 'center', 'marginBottom': '4px',
                }),
                html.Div('Data: 34 Provinsi | 2022–2025', style={
                    'fontSize': '10px', 'color': 'rgba(255,255,255,0.5)',
                    'textAlign': 'center',
                }),
            ], style={'padding': '8px 0'}),

        ], className='sidebar-bottom'),

    ], className='sidebar')
