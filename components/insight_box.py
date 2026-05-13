"""
Insight Box — Dashboard PHK Indonesia
Auto-generated natural language summary dari model Bayesian ST-CAR.
"""
from dash import html


def generate_insight_phk(df, tahun, selected_province=None):
    """
    Generate insight PHK dari data model ST.CARar.

    Parameters
    ----------
    df : DataFrame  — data PHK (kolom: Provinsi, Tahun, RR, PHK, TPAK, IPM)
    tahun : int     — tahun terpilih
    selected_province : str | None
    """
    df_year = df[df['Tahun'] == tahun].copy()
    if df_year.empty:
        return html.Div("Data tidak tersedia.", className='insight-text')

    # ── Metrik utama ──
    avg_rr   = df_year['RR'].mean()
    total_phk = int(df_year['PHK'].sum())
    max_rr_row = df_year.loc[df_year['RR'].idxmax()]
    min_rr_row = df_year.loc[df_year['RR'].idxmin()]
    max_phk_row = df_year.loc[df_year['PHK'].idxmax()]

    prov_max_rr  = max_rr_row['Provinsi']
    val_max_rr   = max_rr_row['RR']
    prov_min_rr  = min_rr_row['Provinsi']
    val_min_rr   = min_rr_row['RR']
    prov_max_phk = max_phk_row['Provinsi']
    val_max_phk  = int(max_phk_row['PHK'])

    # Provinsi RR > 1
    high_risk = df_year[df_year['RR'] > 1.0].sort_values('RR', ascending=False)
    n_high    = len(high_risk)
    list_high = high_risk['Provinsi'].head(4).tolist()

    # YoY PHK
    years = sorted(df['Tahun'].unique())
    if tahun > years[0]:
        df_prev = df[df['Tahun'] == tahun - 1]
        if not df_prev.empty:
            prev_total = int(df_prev['PHK'].sum())
            delta = total_phk - prev_total
        else:
            delta = 0
    else:
        delta = 0

    delta_dir = "kenaikan" if delta > 0 else "penurunan"
    delta_abs = abs(delta)

    # ── Build paragraphs ──
    parts = []

    parts.append(
        f"📌 **Insight Utama ({tahun}):** "
        f"Total PHK nasional tercatat **{total_phk:,} pekerja**, "
        f"dengan **{prov_max_phk}** mencatat jumlah PHK terbesar (**{val_max_phk:,} pekerja**). "
        f"Rata-rata Relative Risk (RR) nasional berada di **{avg_rr:.3f}**."
    )

    if tahun > years[0]:
        parts.append(
            f" Dibandingkan tahun {tahun - 1}, total PHK mengalami "
            f"**{delta_dir}** sebesar **{delta_abs:,} pekerja**."
        )

    parts.append(
        f" Dari sisi model Bayesian, **{prov_max_rr}** memiliki Relative Risk tertinggi "
        f"(**RR = {val_max_rr:.3f}**), menunjukkan risiko PHK jauh di atas rata-rata nasional. "
        f"Sebaliknya, **{prov_min_rr}** memiliki RR terendah (**{val_min_rr:.3f}**)."
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
            tpak_str = f", TPAK **{row['TPAK']:.1f}%**" if 'TPAK' in row and not __import__('math').isnan(row['TPAK']) else ""
            ipm_str  = f", IPM **{row['IPM']:.2f}**" if 'IPM' in row and not __import__('math').isnan(row['IPM']) else ""
            parts.append(
                f"\n\n🔍 **Fokus {selected_province}:** Peringkat ke-**{prov_rank}** dari 34 provinsi "
                f"dengan RR **{row['RR']:.3f}** ({rr_status} rata-rata), "
                f"PHK **{int(row['PHK']):,} pekerja**{tpak_str}{ipm_str}."
            )

    # Render with bold
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
