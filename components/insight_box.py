"""
Insight Box — Dashboard TBC Indonesia
Auto-generated natural language summary dari model INLA.
"""
from dash import html


def generate_insight_tbc(df, tahun, selected_province=None):
    """
    Generate insight TBC dari data model INLA.

    Parameters
    ----------
    df : DataFrame  — tbc_data.csv (kolom: Provinsi, Tahun, Rate_per100k, RR, ...)
    tahun : int     — tahun terpilih
    selected_province : str | None
    """
    df_year = df[df['Tahun'] == tahun].copy()
    if df_year.empty:
        return html.Div("Data tidak tersedia.", className='insight-text')

    # ── Metrik utama ──
    avg_rate = df_year['Rate_per100k'].mean()
    avg_rr   = df_year['RR'].mean()

    max_rate_row = df_year.loc[df_year['Rate_per100k'].idxmax()]
    min_rate_row = df_year.loc[df_year['Rate_per100k'].idxmin()]
    max_rr_row   = df_year.loc[df_year['RR'].idxmax()]

    prov_max_rate = max_rate_row['Provinsi']
    val_max_rate  = max_rate_row['Rate_per100k']
    prov_min_rate = min_rate_row['Provinsi']
    val_min_rate  = min_rate_row['Rate_per100k']
    prov_max_rr   = max_rr_row['Provinsi']
    val_max_rr    = max_rr_row['RR']

    # Provinsi RR > 1
    high_risk = df_year[df_year['RR'] > 1.0].sort_values('RR', ascending=False)
    n_high    = len(high_risk)
    list_high = high_risk['Provinsi'].head(4).tolist()

    # YoY Rate
    if tahun > 2020:
        df_prev = df[df['Tahun'] == tahun - 1]
        if not df_prev.empty:
            prev_avg = df_prev['Rate_per100k'].mean()
            yoy = avg_rate - prev_avg
        else:
            yoy = 0
    else:
        yoy = 0

    yoy_dir = "kenaikan" if yoy > 0 else "penurunan"
    yoy_abs = abs(yoy)

    # ── Build paragraphs ──
    parts = []

    parts.append(
        f"📌 **Insight Utama ({tahun}):** "
        f"**{prov_max_rate}** memiliki Angka Penemuan TBC tertinggi sebesar "
        f"**{val_max_rate:.1f} per 100.000 penduduk**, "
        f"sementara **{prov_min_rate}** paling rendah (**{val_min_rate:.1f}/100.000**). "
        f"Rata-rata nasional berada di **{avg_rate:.1f}/100.000**."
    )

    if tahun > 2020:
        parts.append(
            f" Dibandingkan tahun {tahun - 1}, angka penemuan mengalami "
            f"**{yoy_dir}** sebesar **{yoy_abs:.1f}** per 100.000."
        )

    parts.append(
        f" Dari sisi model Bayesian, **{prov_max_rr}** memiliki Relative Risk tertinggi "
        f"(**RR = {val_max_rr:.3f}**), menunjukkan risiko TBC jauh di atas rata-rata nasional."
    )

    if n_high > 0:
        prov_str = ', '.join(list_high)
        parts.append(
            f" Terdapat **{n_high} provinsi** dengan RR > 1 (risiko di atas rata-rata): "
            f"{prov_str}{'...' if n_high > 4 else ''}."
        )

    # Spesifik provinsi
    if selected_province:
        prov_data = df_year[df_year['Provinsi'] == selected_province]
        if not prov_data.empty:
            row  = prov_data.iloc[0]
            rank = df_year['RR'].rank(ascending=False)
            prov_rank = int(rank[prov_data.index[0]])
            rr_status = "di atas" if row['RR'] > 1.0 else "di bawah"
            parts.append(
                f"\n\n🔍 **Fokus {selected_province}:** Peringkat ke-**{prov_rank}** dari 34 provinsi "
                f"dengan RR **{row['RR']:.3f}** ({rr_status} rata-rata), "
                f"angka penemuan **{row['Rate_per100k']:.1f}/100.000**, "
                f"sanitasi layak **{row['Sanitasi']:.1f}%**."
            )

    # Render
    full_text = ''.join(parts)
    segments  = full_text.split('**')
    children  = []
    for i, seg in enumerate(segments):
        if i % 2 == 1:
            children.append(html.Strong(seg))
        else:
            children.append(seg)

    return html.Div([
        html.Span('💡', className='insight-icon'),
        html.Span(children, className='insight-text'),
    ], className='glass-card insight-box')
