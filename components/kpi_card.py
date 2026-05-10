"""
KPI Card Component — Dashboard TBC Indonesia
White cards with colored icon boxes, values, sparklines, and progress bars.
For TBC context: higher rate/RR = worse (negative), lower = better (positive).
"""
from dash import html, dcc
import dash_bootstrap_components as dbc

from components.chart_utils import create_sparkline

# Icon box color mapping
ICON_COLORS = {
    'juta'    : ('teal',   '#3d8b8a'),
    'persen'  : ('blue',   '#4a8fa8'),
    'rupiah'  : ('amber',  '#5ba4a4'),
    'desimal3': ('rose',   '#7caec4'),
    'kota'    : ('green',  '#80cbc4'),
    'desa'    : ('purple', '#9fc5d5'),
}


def create_kpi_card(card_id, label, value, yoy_change, sparkline_data,
                    icon, fmt='persen', is_critical=False, progress=50):
    """Create a single KPI card with TBC-context change logic.

    For TBC/RR: increase (▲) = negative (bad), decrease (▼) = positive (good).
    yoy_change = 0 → show neutral dash (used for static metrics).
    """
    # Change direction — TBC context: increase in rate/RR is bad
    if yoy_change is None or yoy_change == 0:
        change_text  = '— Data acuan'
        change_class = 'neutral'
    elif yoy_change < 0:
        # Rate/RR turun = BAIK ✅
        change_text  = f'▼ {abs(yoy_change):.1f}% dari tahun lalu'
        change_class = 'positive'
    else:
        # Rate/RR naik = PERHATIAN ⚠️
        change_text  = f'▲ {yoy_change:.1f}% dari tahun lalu'
        change_class = 'negative'

    # Special neutral for sanitasi/air (increase = good)
    if fmt in ('persen',) and card_id in ('san', 'air'):
        if yoy_change and yoy_change > 0:
            change_text  = f'▲ {yoy_change:.1f}% dari tahun lalu'
            change_class = 'positive'
        elif yoy_change and yoy_change < 0:
            change_text  = f'▼ {abs(yoy_change):.1f}% dari tahun lalu'
            change_class = 'negative'

    # Icon box color
    box_class, spark_color = ICON_COLORS.get(fmt, ('teal', '#4db6ac'))

    # Sparkline — skip if all zeros
    if sparkline_data and any(v != 0 for v in sparkline_data):
        sparkline_fig = create_sparkline(sparkline_data, color=spark_color)
        show_spark = True
    else:
        show_spark = False

    # Glow class for critical
    card_classes = 'glass-card kpi-card gradient-border'
    if is_critical:
        card_classes += ' glow-danger'

    spark_el = []
    if show_spark:
        spark_el = [html.Div([
            dcc.Graph(
                figure=sparkline_fig,
                config={'displayModeBar': False},
                style={'height': '30px'},
            ),
        ], className='kpi-sparkline')]

    progress_clamped = max(0, min(100, float(progress)))

    return dbc.Col([
        html.Div([
            # Label row with icon
            html.Div([
                html.Div(icon, className=f'kpi-icon-box {box_class}'),
                html.Span(label),
            ], className='kpi-label'),

            # Value
            html.Div(value, className='kpi-value', id=f'kpi-value-{card_id}'),

            # YoY Change
            html.Div(change_text, className=f'kpi-change {change_class}'),

        ] + spark_el + [

            # Progress bar
            html.Div([
                html.Div(style={'width': f'{progress_clamped:.0f}%'}, className='kpi-progress-fill'),
            ], className='kpi-progress-bar'),

        ], className=card_classes),
    ], lg=2, md=4, sm=6, xs=12)
