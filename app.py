"""
Dashboard Kemiskinan Indonesia — Main Application
Premium Plotly Dash dashboard with 3 pages, dark glassmorphism theme.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

import dash
from dash import html, dcc, callback, Input, Output, State, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc

from components.sidebar import create_sidebar
from pages import overview, trends

# ═══════════════════════════════════════════════════════════════════════
# APP INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title='Dashboard TBC Indonesia',
    update_title='Memuat...',
    meta_tags=[
        {'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'},
        {'name': 'description', 'content': 'Dashboard interaktif kemiskinan Indonesia dengan visualisasi data premium'},
    ],
)

server = app.server

# ═══════════════════════════════════════════════════════════════════════
# TOUR STEPS
# ═══════════════════════════════════════════════════════════════════════

TOUR_STEPS = [
    {
        'title': 'Selamat Datang! 🫁',
        'text': 'Dashboard TBC Indonesia menyajikan hasil analisis model Bayesian '
                'CAR Leroux Spasio-Temporal untuk 34 provinsi periode 2020–2025. '
                'Data mencakup Angka Penemuan TBC, Relative Risk (RR), dan kovariat sosial-ekonomi.',
    },
    {
        'title': 'KPI Cards 📊',
        'text': 'Baris atas menampilkan indikator utama: Angka Penemuan TBC per 100.000 penduduk, '
                'Rata-rata RR nasional, jumlah provinsi dengan RR > 1, dan cakupan sanitasi/air minum. '
                'RR > 1 berarti risiko di atas rata-rata nasional.',
    },
    {
        'title': 'Peta TBC 🗺️',
        'text': 'Peta menampilkan distribusi spasial TBC. Gunakan toggle untuk beralih antara '
                'Relative Risk (RR dari model INLA) dan Angka Penemuan per 100.000 penduduk. '
                'Klik provinsi untuk melihat insight spesifik.',
    },
    {
        'title': 'Diagnostik & Hyperparameter 🔬',
        'text': 'Bagian bawah Overview menampilkan diagnostik model (DIC, WAIC, CPO) '
                'dan hyperparameter posterior model Leroux (ν², τ², ρS, ρT).',
    },
    {
        'title': 'Halaman Tren & Analisis 📈',
        'text': 'Halaman kedua menyajikan tren temporal RR, ranking provinsi, '
                'scatter plot korelasi kovariat vs RR, efek random temporal (RW1), '
                'dan forest plot estimasi fixed effects.',
    },
    {
        'title': 'Selamat Mengeksplorasi! 🚀',
        'text': 'Tekan 1 untuk halaman Overview, 2 untuk Tren & Analisis. '
                'Semua chart interaktif — hover, klik, dan filter untuk eksplorasi mendalam.',
    },
]

# ═══════════════════════════════════════════════════════════════════════
# LAYOUT
# ═══════════════════════════════════════════════════════════════════════

app.layout = html.Div([
    # URL routing
    dcc.Location(id='url', refresh=False),
    
    # Shared stores
    dcc.Store(id='selected-province', data=None),
    dcc.Store(id='tour-step', data=0),
    dcc.Store(id='tour-active', data=False),
    
    # Sidebar
    create_sidebar(),
    
    # Page content
    html.Div(id='page-content', className='main-content'),
    
    # ── Keyboard Shortcuts Modal ──
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('⌨️ Keyboard Shortcuts')),
        dbc.ModalBody([
            html.Table([
                html.Tr([
                    html.Td(html.Span('1', className='shortcut-key')),
                    html.Td('Buka halaman Overview'),
                ]),
                html.Tr([
                    html.Td(html.Span('2', className='shortcut-key')),
                    html.Td('Buka halaman Tren & Perbandingan'),
                ]),
                html.Tr([
                    html.Td(html.Span('3', className='shortcut-key')),
                    html.Td('Buka halaman Analisis & Korelasi'),
                ]),
                html.Tr([
                    html.Td(html.Span('R', className='shortcut-key')),
                    html.Td('Reset semua filter'),
                ]),
                html.Tr([
                    html.Td(html.Span('?', className='shortcut-key')),
                    html.Td('Tampilkan/sembunyikan panel ini'),
                ]),
            ], className='shortcut-table'),
        ]),
        dbc.ModalFooter(
            dbc.Button('Tutup', id='close-shortcut-modal', className='tour-btn tour-btn-next',
                       n_clicks=0),
        ),
    ], id='shortcut-modal', is_open=False, centered=True),
    
    # ── Tour Modal ──
    dbc.Modal([
        dbc.ModalBody([
            html.Div(id='tour-content'),
        ]),
        dbc.ModalFooter([
            html.Div(id='tour-step-indicator', className='tour-step-indicator',
                     style={'marginRight': 'auto'}),
            dbc.Button('← Sebelumnya', id='tour-prev', className='tour-btn tour-btn-prev',
                       n_clicks=0),
            dbc.Button('Selanjutnya →', id='tour-next', className='tour-btn tour-btn-next',
                       n_clicks=0),
        ]),
    ], id='tour-modal', is_open=False, centered=True, size='lg'),
    
    # ── About Modal ──
    dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle('ℹ️ Tentang Dashboard TBC Indonesia')),
        dbc.ModalBody([
            html.P([
                'Dashboard ini menyajikan hasil analisis model ',
                html.Strong('Bayesian Spasio-Temporal CAR Leroux'),
                ' untuk data Tuberkulosis (TBC) 34 provinsi Indonesia periode 2020–2025.',
            ], style={'lineHeight': '1.7', 'color': '#475569'}),
            html.P([
                'Model dibangun menggunakan paket ', html.Strong('R-INLA'),
                ' dengan struktur Poisson likelihood, efek spasial Leroux, '
                'efek temporal RW1, dan interaksi spasio-temporal IID.',
            ], style={'lineHeight': '1.7', 'color': '#475569'}),
            html.Hr(style={'borderColor': '#e8eff4'}),
            html.P([
                '📊 Data: BPS & Kemenkes RI | '
                '🔧 Tools: R-INLA, Plotly Dash | '
                '📅 Periode: 2020–2025',
            ], style={'fontSize': '13px', 'color': '#94a3b8'}),
        ]),
        dbc.ModalFooter(
            dbc.Button('Tutup', id='close-about-modal', className='tour-btn tour-btn-next',
                       n_clicks=0),
        ),
    ], id='about-modal', is_open=False, centered=True),
    
    # Hidden divs for clientside callbacks
    html.Div(id='keyboard-listener', style={'display': 'none'}),
    html.Div(id='tilt-listener', style={'display': 'none'}),
    html.Div(id='countup-listener', style={'display': 'none'}),
    
], style={'minHeight': '100vh', 'background': '#dae5ec'})


# ═══════════════════════════════════════════════════════════════════════
# CALLBACKS
# ═══════════════════════════════════════════════════════════════════════

# ── Page Routing ──
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
)
def display_page(pathname):
    """Route to the correct page based on URL."""
    if pathname == '/trends':
        return trends.layout()
    else:
        return overview.layout()


# ── Active Sidebar Link + Sliding Indicator ──
app.clientside_callback(
    """
    function(pathname) {
        const base = 'sidebar-link';
        const active = 'sidebar-link active';

        let overviewCls = base, trendsCls = base;
        let targetId = 'nav-overview';

        if (pathname === '/trends') {
            trendsCls = active;
            targetId = 'nav-trends';
        } else {
            overviewCls = active;
            targetId = 'nav-overview';
        }

        setTimeout(function() {
            const target = document.getElementById(targetId);
            const indicator = document.getElementById('nav-indicator');
            const navContainer = target?.closest('.sidebar-nav');
            if (target && indicator && navContainer) {
                const navRect = navContainer.getBoundingClientRect();
                const targetRect = target.getBoundingClientRect();
                indicator.style.top = (targetRect.top - navRect.top) + 'px';
                indicator.style.height = targetRect.height + 'px';
            }
        }, 10);

        return [overviewCls, trendsCls, {}];
    }
    """,
    Output('nav-overview', 'className'),
    Output('nav-trends', 'className'),
    Output('nav-indicator', 'style'),
    Input('url', 'pathname'),
)


# ── About Modal ──
@callback(
    Output('about-modal', 'is_open'),
    Input('btn-about', 'n_clicks'),
    Input('close-about-modal', 'n_clicks'),
    State('about-modal', 'is_open'),
    prevent_initial_call=True,
)
def toggle_about_modal(n1, n2, is_open):
    return not is_open


# ── Shortcut Modal ──
@callback(
    Output('shortcut-modal', 'is_open'),
    Input('close-shortcut-modal', 'n_clicks'),
    State('shortcut-modal', 'is_open'),
    prevent_initial_call=True,
)
def toggle_shortcut_modal(n, is_open):
    return not is_open


# ── Tour ──
@callback(
    Output('tour-modal', 'is_open'),
    Output('tour-content', 'children'),
    Output('tour-step-indicator', 'children'),
    Output('tour-next', 'children'),
    Input('btn-start-tour', 'n_clicks'),
    Input('tour-next', 'n_clicks'),
    Input('tour-prev', 'n_clicks'),
    State('tour-modal', 'is_open'),
    State('tour-step', 'data'),
    prevent_initial_call=True,
)
def manage_tour(start_clicks, next_clicks, prev_clicks, is_open, current_step):
    """Manage tour modal state and navigation."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return False, '', '', 'Selanjutnya →'
    
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger == 'btn-start-tour':
        step = 0
    elif trigger == 'tour-next':
        step = (current_step or 0) + 1
        if step >= len(TOUR_STEPS):
            return False, '', '', 'Selanjutnya →'
    elif trigger == 'tour-prev':
        step = max(0, (current_step or 0) - 1)
    else:
        step = current_step or 0
    
    tour = TOUR_STEPS[step]
    content = html.Div([
        html.H4(tour['title'], style={
            'fontFamily': 'Outfit', 'fontWeight': '600', 'marginBottom': '16px',
            'color': '#e2e8f0',
        }),
        html.P(tour['text'], className='tour-text'),
    ])
    
    indicator = f'{step + 1}/{len(TOUR_STEPS)}'
    btn_text = 'Selesai 🎉' if step == len(TOUR_STEPS) - 1 else 'Selanjutnya →'
    
    return True, content, indicator, btn_text


@callback(
    Output('tour-step', 'data'),
    Input('tour-next', 'n_clicks'),
    Input('tour-prev', 'n_clicks'),
    Input('btn-start-tour', 'n_clicks'),
    State('tour-step', 'data'),
    prevent_initial_call=True,
)
def update_tour_step(next_n, prev_n, start_n, current):
    """Track current tour step."""
    ctx = dash.callback_context
    if not ctx.triggered:
        return 0
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger == 'btn-start-tour':
        return 0
    elif trigger == 'tour-next':
        return min((current or 0) + 1, len(TOUR_STEPS) - 1)
    elif trigger == 'tour-prev':
        return max(0, (current or 0) - 1)
    return current or 0


# ═══════════════════════════════════════════════════════════════════════
# CLIENTSIDE CALLBACKS
# ═══════════════════════════════════════════════════════════════════════

# ── Keyboard Shortcuts ──
app.clientside_callback(
    """
    function(pathname) {
        if (window._keyboardListenerAdded) return window.dash_clientside.no_update;
        window._keyboardListenerAdded = true;
        
        document.addEventListener('keydown', function(e) {
            // Don't trigger when typing in inputs
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') {
                return;
            }
            
            if (e.key === '1') {
                window.history.pushState({}, '', '/');
                window.dispatchEvent(new PopStateEvent('popstate'));
            } else if (e.key === '2') {
                window.history.pushState({}, '', '/trends');
                window.dispatchEvent(new PopStateEvent('popstate'));
            } else if (e.key === '3') {
                window.history.pushState({}, '', '/analysis');
                window.dispatchEvent(new PopStateEvent('popstate'));
            } else if (e.key === '?') {
                var modal = document.getElementById('shortcut-modal');
                if (modal) {
                    // Toggle via click on close button
                    var closeBtn = document.getElementById('close-shortcut-modal');
                    if (closeBtn) closeBtn.click();
                }
            }
        });
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('keyboard-listener', 'children'),
    Input('url', 'pathname'),
)

# ── 3D Tilt Effect on KPI Cards ──
app.clientside_callback(
    """
    function(pathname) {
        setTimeout(function() {
            var cards = document.querySelectorAll('.kpi-card');
            cards.forEach(function(card) {
                if (card._tiltAdded) return;
                card._tiltAdded = true;
                
                card.addEventListener('mousemove', function(e) {
                    var rect = card.getBoundingClientRect();
                    var x = e.clientX - rect.left;
                    var y = e.clientY - rect.top;
                    var centerX = rect.width / 2;
                    var centerY = rect.height / 2;
                    var rotateX = (y - centerY) / centerY * -5;
                    var rotateY = (x - centerX) / centerX * 5;
                    
                    card.style.transform = 'perspective(1000px) rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg) translateY(-2px)';
                });
                
                card.addEventListener('mouseleave', function() {
                    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
                });
            });
        }, 1000);
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('tilt-listener', 'children'),
    Input('page-content', 'children'),
)

# ── Animated Count-Up on KPI Values ──
app.clientside_callback(
    """
    function(children) {
        setTimeout(function() {
            var kpiElements = document.querySelectorAll('[id^="kpi-value-"]');
            
            kpiElements.forEach(function(el) {
                if (el._animated) return;
                el._animated = true;
                
                var text = el.textContent.trim();
                var originalText = text;
                
                // Extract numeric value
                var numStr = text.replace(/[^0-9.,]/g, '').replace(/\\./g, '').replace(',', '.');
                var targetVal = parseFloat(numStr);
                
                if (isNaN(targetVal) || targetVal === 0) return;
                
                var prefix = '';
                var suffix = '';
                
                // Detect format
                if (text.includes('Rp')) prefix = 'Rp ';
                if (text.includes('%')) suffix = '%';
                if (text.includes('Juta')) suffix = ' Juta';
                
                var duration = 1500;
                var startTime = null;
                
                function easeOutQuart(t) {
                    return 1 - Math.pow(1 - t, 4);
                }
                
                function formatNumber(val) {
                    if (suffix === ' Juta') {
                        return prefix + val.toFixed(1) + suffix;
                    } else if (suffix === '%') {
                        return prefix + val.toFixed(2) + suffix;
                    } else if (prefix === 'Rp ') {
                        return prefix + Math.round(val).toLocaleString('id-ID');
                    } else if (originalText.includes('.') && !originalText.includes(',')) {
                        var decimals = (originalText.split('.')[1] || '').length;
                        return val.toFixed(Math.min(decimals, 3));
                    }
                    return prefix + val.toFixed(2) + suffix;
                }
                
                function step(timestamp) {
                    if (!startTime) startTime = timestamp;
                    var progress = Math.min((timestamp - startTime) / duration, 1);
                    var easedProgress = easeOutQuart(progress);
                    var currentVal = targetVal * easedProgress;
                    
                    el.textContent = formatNumber(currentVal);
                    
                    if (progress < 1) {
                        requestAnimationFrame(step);
                    } else {
                        el.textContent = originalText;
                    }
                }
                
                el.textContent = formatNumber(0);
                requestAnimationFrame(step);
            });
        }, 300);
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('countup-listener', 'children'),
    Input('page-content', 'children'),
)


# ═══════════════════════════════════════════════════════════════════════
# RUN SERVER
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
