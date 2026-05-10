"""
Data dummy realistis: 34 provinsi × 7 tahun (2018-2024) untuk Dashboard Kemiskinan Indonesia.
Menggunakan nama provinsi yang match dengan shapefile BPS 2020.
"""

import pandas as pd
import numpy as np

# ─── Target Nasional ─────────────────────────────────────────────────────
TARGET_RPJMN = {2020: 8.5, 2021: 8.0, 2022: 7.5, 2023: 7.0, 2024: 6.5}
TARGET_SDGS_2030 = 4.0

# ─── Mapping Provinsi → Pulau ────────────────────────────────────────────
PROVINSI_PULAU = {
    'Aceh': 'Sumatera',
    'Sumatera Utara': 'Sumatera',
    'Sumatera Barat': 'Sumatera',
    'Riau': 'Sumatera',
    'Jambi': 'Sumatera',
    'Sumatera Selatan': 'Sumatera',
    'Bengkulu': 'Sumatera',
    'Lampung': 'Sumatera',
    'Kepulauan Bangka Belitung': 'Sumatera',
    'Kepulauan Riau': 'Sumatera',
    'Dki Jakarta': 'Jawa',
    'Jawa Barat': 'Jawa',
    'Jawa Tengah': 'Jawa',
    'Daerah Istimewa Yogyakarta': 'Jawa',
    'Jawa Timur': 'Jawa',
    'Banten': 'Jawa',
    'Bali': 'Bali & Nusa Tenggara',
    'Nusa Tenggara Barat': 'Bali & Nusa Tenggara',
    'Nusa Tenggara Timur': 'Bali & Nusa Tenggara',
    'Kalimantan Barat': 'Kalimantan',
    'Kalimantan Tengah': 'Kalimantan',
    'Kalimantan Selatan': 'Kalimantan',
    'Kalimantan Timur': 'Kalimantan',
    'Kalimantan Utara': 'Kalimantan',
    'Sulawesi Utara': 'Sulawesi',
    'Sulawesi Tengah': 'Sulawesi',
    'Sulawesi Selatan': 'Sulawesi',
    'Sulawesi Tenggara': 'Sulawesi',
    'Gorontalo': 'Sulawesi',
    'Sulawesi Barat': 'Sulawesi',
    'Maluku': 'Maluku',
    'Maluku Utara': 'Maluku',
    'Papua': 'Papua',
    'Papua Barat': 'Papua',
}

# ─── Koordinat per Provinsi (untuk scatter_mapbox) ─────────────────────
KOORDINAT_PROVINSI = {
    'Aceh': (4.695, 96.749),
    'Sumatera Utara': (2.116, 99.545),
    'Sumatera Barat': (-0.739, 100.800),
    'Riau': (1.009, 102.148),
    'Jambi': (-1.611, 103.613),
    'Sumatera Selatan': (-3.319, 104.914),
    'Bengkulu': (-3.793, 102.260),
    'Lampung': (-4.556, 105.406),
    'Kepulauan Bangka Belitung': (-2.741, 106.440),
    'Kepulauan Riau': (3.946, 108.143),
    'Dki Jakarta': (-6.208, 106.846),
    'Jawa Barat': (-6.921, 107.608),
    'Jawa Tengah': (-7.151, 110.140),
    'Daerah Istimewa Yogyakarta': (-7.797, 110.369),
    'Jawa Timur': (-7.536, 112.238),
    'Banten': (-6.405, 106.064),
    'Bali': (-8.350, 115.175),
    'Nusa Tenggara Barat': (-8.652, 117.362),
    'Nusa Tenggara Timur': (-8.657, 121.079),
    'Kalimantan Barat': (-0.279, 109.134),
    'Kalimantan Tengah': (-1.682, 113.382),
    'Kalimantan Selatan': (-3.092, 115.283),
    'Kalimantan Timur': (1.693, 116.419),
    'Kalimantan Utara': (3.073, 116.911),
    'Sulawesi Utara': (0.625, 123.975),
    'Sulawesi Tengah': (-1.431, 121.446),
    'Sulawesi Selatan': (-3.668, 119.974),
    'Sulawesi Tenggara': (-4.145, 122.175),
    'Gorontalo': (0.696, 122.455),
    'Sulawesi Barat': (-2.844, 119.232),
    'Maluku': (-3.239, 130.145),
    'Maluku Utara': (1.571, 127.809),
    'Papua': (-4.269, 138.080),
    'Papua Barat': (-1.336, 133.174),
}

# ─── Baseline kemiskinan 2018 per provinsi (realistis) ───────────────────
# Tinggi di Papua/Maluku/NTT, rendah di DKI/Bali/Kaltim
_BASELINE_KEMISKINAN = {
    'Aceh': 15.97, 'Sumatera Utara': 9.22, 'Sumatera Barat': 6.55,
    'Riau': 7.39, 'Jambi': 7.85, 'Sumatera Selatan': 12.82,
    'Bengkulu': 15.41, 'Lampung': 13.01, 'Kepulauan Bangka Belitung': 4.77,
    'Kepulauan Riau': 5.83, 'Dki Jakarta': 3.55, 'Jawa Barat': 7.45,
    'Jawa Tengah': 11.32, 'Daerah Istimewa Yogyakarta': 11.81,
    'Jawa Timur': 10.85, 'Banten': 5.25, 'Bali': 3.91,
    'Nusa Tenggara Barat': 14.63, 'Nusa Tenggara Timur': 21.03,
    'Kalimantan Barat': 7.77, 'Kalimantan Tengah': 5.10,
    'Kalimantan Selatan': 4.65, 'Kalimantan Timur': 6.03,
    'Kalimantan Utara': 6.86, 'Sulawesi Utara': 7.59,
    'Sulawesi Tengah': 13.69, 'Sulawesi Selatan': 8.87,
    'Sulawesi Tenggara': 11.32, 'Gorontalo': 15.83, 'Sulawesi Barat': 11.22,
    'Maluku': 17.85, 'Maluku Utara': 6.62,
    'Papua': 27.43, 'Papua Barat': 22.66,
}

# ─── Baseline IPM 2018 per provinsi ─────────────────────────────────────
_BASELINE_IPM = {
    'Aceh': 71.19, 'Sumatera Utara': 71.18, 'Sumatera Barat': 71.73,
    'Riau': 72.44, 'Jambi': 70.65, 'Sumatera Selatan': 68.86,
    'Bengkulu': 69.95, 'Lampung': 69.02, 'Kepulauan Bangka Belitung': 70.67,
    'Kepulauan Riau': 74.84, 'Dki Jakarta': 80.47, 'Jawa Barat': 71.30,
    'Jawa Tengah': 71.12, 'Daerah Istimewa Yogyakarta': 79.53,
    'Jawa Timur': 70.77, 'Banten': 71.95, 'Bali': 75.28,
    'Nusa Tenggara Barat': 66.58, 'Nusa Tenggara Timur': 63.73,
    'Kalimantan Barat': 66.98, 'Kalimantan Tengah': 69.79,
    'Kalimantan Selatan': 70.17, 'Kalimantan Timur': 75.83,
    'Kalimantan Utara': 70.56, 'Sulawesi Utara': 72.20,
    'Sulawesi Tengah': 68.88, 'Sulawesi Selatan': 70.90,
    'Sulawesi Tenggara': 69.86, 'Gorontalo': 67.71, 'Sulawesi Barat': 64.63,
    'Maluku': 68.19, 'Maluku Utara': 67.76,
    'Papua': 60.06, 'Papua Barat': 62.99,
}


def generate_data():
    """Generate data dummy 34 provinsi × 7 tahun = 238 baris."""
    np.random.seed(42)
    
    tahun_list = list(range(2018, 2025))
    records = []
    
    for prov, pulau in PROVINSI_PULAU.items():
        base_kemiskinan = _BASELINE_KEMISKINAN[prov]
        base_ipm = _BASELINE_IPM[prov]
        
        for i, tahun in enumerate(tahun_list):
            # ── Persentase Kemiskinan ──
            # Trend turun gradual, kecuali 2020 naik (COVID)
            if tahun == 2018:
                pct = base_kemiskinan
            elif tahun == 2019:
                pct = base_kemiskinan - np.random.uniform(0.3, 0.7)
            elif tahun == 2020:
                # COVID spike
                pct = base_kemiskinan + np.random.uniform(0.5, 1.5)
            elif tahun == 2021:
                pct = base_kemiskinan + np.random.uniform(0.0, 0.5)
            else:
                # 2022-2024: gradual decrease
                decrease = (tahun - 2021) * np.random.uniform(0.3, 0.8)
                pct = base_kemiskinan - decrease
            
            pct = max(pct, 2.5)  # floor
            pct += np.random.uniform(-0.3, 0.3)  # noise
            pct = round(pct, 2)
            
            # ── Jumlah Penduduk Miskin ──
            # Populasi approx per provinsi tiered
            if prov in ['Jawa Barat', 'Jawa Timur', 'Jawa Tengah']:
                pop_base = np.random.uniform(3_000_000, 4_500_000)
            elif prov in ['Sumatera Utara', 'Lampung', 'Sumatera Selatan']:
                pop_base = np.random.uniform(800_000, 1_800_000)
            elif prov in ['Dki Jakarta', 'Banten', 'Bali']:
                pop_base = np.random.uniform(300_000, 600_000)
            elif prov in ['Papua', 'Papua Barat', 'Nusa Tenggara Timur']:
                pop_base = np.random.uniform(500_000, 1_200_000)
            elif prov in ['Maluku', 'Maluku Utara', 'Gorontalo', 'Sulawesi Barat',
                          'Kalimantan Utara', 'Kepulauan Bangka Belitung']:
                pop_base = np.random.uniform(50_000, 200_000)
            else:
                pop_base = np.random.uniform(200_000, 800_000)
            
            jumlah = int(pop_base * (pct / 10.0))
            
            # ── Garis Kemiskinan ──
            gk_base = 350_000 + (tahun - 2018) * np.random.uniform(30_000, 50_000)
            if prov in ['Dki Jakarta', 'Bali', 'Kalimantan Timur', 'Kepulauan Riau']:
                gk_base += np.random.uniform(50_000, 100_000)
            garis_kemiskinan = int(gk_base + np.random.uniform(-10_000, 10_000))
            
            # ── Indeks Kedalaman P1 ──
            p1 = pct * np.random.uniform(0.12, 0.22)
            p1 = round(max(p1, 0.3), 2)
            
            # ── Indeks Keparahan P2 ──
            p2 = p1 * np.random.uniform(0.15, 0.35)
            p2 = round(max(p2, 0.05), 2)
            
            # ── Gini Ratio ──
            # DKI, Jabar, DIY cenderung tinggi
            if prov in ['Dki Jakarta', 'Jawa Barat', 'Daerah Istimewa Yogyakarta', 'Gorontalo']:
                gini = np.random.uniform(0.37, 0.42)
            elif prov in ['Papua', 'Papua Barat', 'Maluku']:
                gini = np.random.uniform(0.36, 0.41)
            elif prov in ['Kepulauan Bangka Belitung', 'Kalimantan Tengah']:
                gini = np.random.uniform(0.28, 0.32)
            else:
                gini = np.random.uniform(0.30, 0.38)
            gini = round(gini, 3)
            
            # ── IPM ──
            ipm = base_ipm + (tahun - 2018) * np.random.uniform(0.3, 0.6)
            if tahun == 2020:
                ipm -= np.random.uniform(0.1, 0.3)
            ipm = round(ipm + np.random.uniform(-0.2, 0.2), 2)
            
            # ── Pengangguran ──
            if prov in ['Dki Jakarta', 'Jawa Barat', 'Banten']:
                unemp = np.random.uniform(7.0, 9.0)
            elif prov in ['Bali', 'Kalimantan Tengah', 'Nusa Tenggara Timur']:
                unemp = np.random.uniform(2.5, 4.5)
            else:
                unemp = np.random.uniform(3.5, 7.0)
            if tahun == 2020:
                unemp += np.random.uniform(1.0, 2.5)
            unemp = round(unemp, 2)
            
            # ── Rata-rata Lama Sekolah ──
            if prov in ['Dki Jakarta']:
                rls = np.random.uniform(10.5, 11.5)
            elif prov in ['Papua', 'Papua Barat', 'Nusa Tenggara Timur']:
                rls = np.random.uniform(5.5, 7.5)
            else:
                rls = np.random.uniform(7.5, 10.0)
            rls += (tahun - 2018) * 0.1
            rls = round(rls, 2)
            
            # ── Pengeluaran per Kapita (Rp ribu/bulan) ──
            if prov in ['Dki Jakarta', 'Bali', 'Kalimantan Timur']:
                pengeluaran = int(np.random.uniform(14_000, 18_000))
            elif prov in ['Papua', 'Nusa Tenggara Timur', 'Maluku']:
                pengeluaran = int(np.random.uniform(6_000, 9_000))
            else:
                pengeluaran = int(np.random.uniform(8_000, 14_000))
            pengeluaran += int((tahun - 2018) * np.random.uniform(200, 500))
            
            # ── Kemiskinan Kota & Desa ──
            kemiskinan_kota = round(pct * np.random.uniform(0.55, 0.75), 2)
            kemiskinan_desa = round(pct * np.random.uniform(1.2, 1.6), 2)
            # Ensure desa > kota
            if kemiskinan_desa <= kemiskinan_kota:
                kemiskinan_desa = kemiskinan_kota + np.random.uniform(2.0, 5.0)
            kemiskinan_kota = max(kemiskinan_kota, 2.5)
            kemiskinan_desa = max(kemiskinan_desa, 5.0)
            
            # ── Penerima Bansos ──
            bansos_base = jumlah * np.random.uniform(0.5, 0.9)
            if tahun >= 2020:
                bansos_base *= np.random.uniform(1.2, 1.5)
            penerima_bansos = int(bansos_base)
            
            records.append({
                'tahun': tahun,
                'provinsi': prov,
                'pulau': pulau,
                'jumlah_penduduk_miskin': jumlah,
                'persentase_kemiskinan': pct,
                'garis_kemiskinan': garis_kemiskinan,
                'indeks_kedalaman_p1': p1,
                'indeks_keparahan_p2': p2,
                'gini_ratio': gini,
                'ipm': ipm,
                'pengangguran': unemp,
                'rata_lama_sekolah': rls,
                'pengeluaran_perkapita': pengeluaran,
                'kemiskinan_kota': kemiskinan_kota,
                'kemiskinan_desa': kemiskinan_desa,
                'penerima_bansos': penerima_bansos,
            })
    
    df = pd.DataFrame(records)
    return df


def get_national_aggregates(df):
    """Hitung agregat nasional per tahun."""
    agg = df.groupby('tahun').agg(
        total_penduduk_miskin=('jumlah_penduduk_miskin', 'sum'),
        rata_kemiskinan=('persentase_kemiskinan', 'mean'),
        rata_gini=('gini_ratio', 'mean'),
        rata_kemiskinan_kota=('kemiskinan_kota', 'mean'),
        rata_kemiskinan_desa=('kemiskinan_desa', 'mean'),
        rata_ipm=('ipm', 'mean'),
        rata_pengangguran=('pengangguran', 'mean'),
        rata_pengeluaran=('pengeluaran_perkapita', 'mean'),
        total_bansos=('penerima_bansos', 'sum'),
    ).reset_index()
    return agg


# ─── Color Palette ────────────────────────────────────────────────────────
COLORS = {
    # Background
    'bg_primary': '#0a0e27',
    'bg_secondary': '#0f1b3d',
    'bg_card': 'rgba(255,255,255,0.05)',
    'bg_card_hover': 'rgba(255,255,255,0.08)',
    
    # Accent
    'accent_teal': '#00d4aa',
    'accent_blue': '#3b82f6',
    'accent_purple': '#8b5cf6',
    'accent_cyan': '#06b6d4',
    
    # Status
    'danger': '#ef4444',
    'success': '#22c55e',
    'warning': '#f59e0b',
    
    # Text
    'text_primary': '#e2e8f0',
    'text_secondary': '#94a3b8',
    'text_muted': '#64748b',
    
    # Chart
    'chart_bg': 'rgba(0,0,0,0)',
    'chart_grid': 'rgba(255,255,255,0.05)',
    'chart_sequence': ['#3d8b8a', '#5ba4a4', '#7ab8b8', '#4a8fa8', '#7caec4', '#9fc5d5', '#b8d4e3'],
    
    # Gradient
    'gradient_teal_blue': 'linear-gradient(135deg, #00d4aa, #3b82f6)',
    'gradient_danger': 'linear-gradient(135deg, #ef4444, #f59e0b)',
}
