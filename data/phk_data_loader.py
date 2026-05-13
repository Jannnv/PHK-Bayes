"""
phk_data_loader.py — Data loader untuk Dashboard PHK Indonesia
Membaca dari Hasil_Model_PHK.xlsx dan DATA NACOESTA.xlsx.
"""
import os
import pandas as pd
import numpy as np

_DIR = os.path.dirname(__file__)

# Excel files committed to data/ directory alongside this loader
_HASIL_MODEL   = os.path.join(_DIR, 'Hasil_Model_PHK.xlsx')
_DATA_NACOESTA = os.path.join(_DIR, 'DATA NACOESTA.xlsx')

YEARS = [2022, 2023, 2024, 2025]


# ── Load data utama ──────────────────────────────────────────────────────────
def load_phk_data():
    """Load data PHK per provinsi per tahun (136 baris: 34 prov × 4 tahun)."""

    # --- Read RR ---
    df_rr = pd.read_excel(_HASIL_MODEL, sheet_name='Relative Risk')
    rr_long = df_rr.melt(id_vars='ADM1_EN', var_name='col', value_name='RR')
    rr_long['Tahun'] = rr_long['col'].str.extract(r'(\d{4})').astype(int)
    rr_long = rr_long.rename(columns={'ADM1_EN': 'Provinsi'})[['Provinsi', 'Tahun', 'RR']]

    # --- Read PHK (Observed Y) ---
    df_y = pd.read_excel(_HASIL_MODEL, sheet_name='Observed Count (Y)')
    y_long = df_y.melt(id_vars='ADM1_EN', var_name='col', value_name='PHK')
    y_long['Tahun'] = y_long['col'].str.extract(r'(\d{4})').astype(int)
    y_long = y_long.rename(columns={'ADM1_EN': 'Provinsi'})[['Provinsi', 'Tahun', 'PHK']]

    # --- Read Expected (E) ---
    df_e = pd.read_excel(_HASIL_MODEL, sheet_name='Expected Count (E)')
    e_long = df_e.melt(id_vars='ADM1_EN', var_name='col', value_name='E')
    e_long['Tahun'] = e_long['col'].str.extract(r'(\d{4})').astype(int)
    e_long = e_long.rename(columns={'ADM1_EN': 'Provinsi'})[['Provinsi', 'Tahun', 'E']]

    # --- Read SMR ---
    df_smr = pd.read_excel(_HASIL_MODEL, sheet_name='SMR')
    smr_long = df_smr.melt(id_vars='ADM1_EN', var_name='col', value_name='SMR')
    smr_long['Tahun'] = smr_long['col'].str.extract(r'(\d{4})').astype(int)
    smr_long = smr_long.rename(columns={'ADM1_EN': 'Provinsi'})[['Provinsi', 'Tahun', 'SMR']]

    # --- Merge all ---
    df = rr_long.merge(y_long, on=['Provinsi', 'Tahun'])
    df = df.merge(e_long, on=['Provinsi', 'Tahun'])
    df = df.merge(smr_long, on=['Provinsi', 'Tahun'])

    # --- Read TPAK & IPM from DATA NACOESTA ---
    try:
        df_raw = pd.read_excel(_DATA_NACOESTA)
        # Map province names from DATA NACOESTA → Hasil_Model_PHK format
        _NAME_MAP = {
            'DI. Yogyakarta': 'Daerah Istimewa Yogyakarta',
            'DKI Jakarta': 'Dki Jakarta',
            'Bangka Belitung': 'Kepulauan Bangka Belitung',
        }
        def clean_name(s):
            s = str(s).strip()
            if s in _NAME_MAP:
                return _NAME_MAP[s]
            return s

        # Build TPAK long
        tpak_cols = {f'TPAK{y}': y for y in YEARS}
        ipm_cols = {f'IPM{y}': y for y in YEARS}

        for col_dict, var_name in [(tpak_cols, 'TPAK'), (ipm_cols, 'IPM')]:
            available = {c: yr for c, yr in col_dict.items() if c in df_raw.columns}
            if available:
                prov_col = 'Provinsi' if 'Provinsi' in df_raw.columns else df_raw.columns[0]
                subset = df_raw[[prov_col] + list(available.keys())].copy()
                subset[prov_col] = subset[prov_col].apply(clean_name)
                melted = subset.melt(id_vars=prov_col, var_name='col', value_name=var_name)
                melted['Tahun'] = melted['col'].str.extract(r'(\d{4})').astype(int)
                melted = melted.rename(columns={prov_col: 'Provinsi'})[[
                    'Provinsi', 'Tahun', var_name
                ]]
                df = df.merge(melted, on=['Provinsi', 'Tahun'], how='left')
    except Exception as e:
        print(f"Warning: Could not load TPAK/IPM from DATA NACOESTA: {e}")
        df['TPAK'] = np.nan
        df['IPM'] = np.nan

    # Add Pulau mapping
    df['Pulau'] = df['Provinsi'].map(PROVINSI_PULAU).fillna('Lainnya')

    # Sort
    df = df.sort_values(['Provinsi', 'Tahun']).reset_index(drop=True)
    df['Tahun'] = df['Tahun'].astype(int)

    return df


def load_fixed_effects():
    """Load hasil estimasi fixed effects (kovariat) model ST.CARar."""
    return pd.read_excel(_HASIL_MODEL, sheet_name='Fixed Effects (Kovariat)')


def load_hyperparameter():
    """Load posterior hyperparameter model."""
    return pd.read_excel(_HASIL_MODEL, sheet_name='Hyperparameter')


def load_diagnostik():
    """Load diagnostik model (DIC, p.d, LMPL)."""
    return pd.read_excel(_HASIL_MODEL, sheet_name='Diagnostik Model')


def load_phi():
    """Load efek spasio-temporal phi per provinsi per tahun."""
    return pd.read_excel(_HASIL_MODEL, sheet_name='Efek Spasio-Temporal phi')


def load_rr_avg():
    """Load RR rata-rata per provinsi."""
    return pd.read_excel(_HASIL_MODEL, sheet_name='RR Rata-rata per Provinsi')


# ── Mapping ──────────────────────────────────────────────────────────────────
PROVINSI_PULAU = {
    'Aceh': 'Sumatera', 'Sumatera Utara': 'Sumatera', 'Sumatera Barat': 'Sumatera',
    'Riau': 'Sumatera', 'Jambi': 'Sumatera', 'Sumatera Selatan': 'Sumatera',
    'Bengkulu': 'Sumatera', 'Lampung': 'Sumatera',
    'Kepulauan Bangka Belitung': 'Sumatera', 'Kepulauan Riau': 'Sumatera',
    'Dki Jakarta': 'Jawa', 'Jawa Barat': 'Jawa', 'Jawa Tengah': 'Jawa',
    'Daerah Istimewa Yogyakarta': 'Jawa', 'Jawa Timur': 'Jawa', 'Banten': 'Jawa',
    'Bali': 'Bali & Nusa Tenggara', 'Nusa Tenggara Barat': 'Bali & Nusa Tenggara',
    'Nusa Tenggara Timur': 'Bali & Nusa Tenggara',
    'Kalimantan Barat': 'Kalimantan', 'Kalimantan Tengah': 'Kalimantan',
    'Kalimantan Selatan': 'Kalimantan', 'Kalimantan Timur': 'Kalimantan',
    'Kalimantan Utara': 'Kalimantan',
    'Sulawesi Utara': 'Sulawesi', 'Sulawesi Tengah': 'Sulawesi',
    'Sulawesi Selatan': 'Sulawesi', 'Sulawesi Tenggara': 'Sulawesi',
    'Gorontalo': 'Sulawesi', 'Sulawesi Barat': 'Sulawesi',
    'Maluku': 'Maluku & Papua', 'Maluku Utara': 'Maluku & Papua',
    'Papua': 'Maluku & Papua', 'Papua Barat': 'Maluku & Papua',
}

# ── Color Palette ─────────────────────────────────────────────────────────────
COLORS = {
    'accent_orange': '#FF5500',
    'accent_amber' : '#FF8F00',
    'accent_yellow': '#FFC800',
    'accent_red'   : '#FF0000',
    'danger'       : '#FF0000',
    'success'      : '#16a34a',
    'warning'      : '#FF7200',
    'text_primary' : '#1e293b',
    'text_secondary': '#475569',
    'text_muted'   : '#94a3b8',
    # Orange gradient chart sequence
    'chart_sequence': ['#FFC800', '#FFB300', '#FF9E00', '#FF8F00',
                       '#FF7200', '#FF5500', '#FF3D00', '#FF0000',
                       '#E60000', '#CC0000'],
}


# ── Computed aggregates ───────────────────────────────────────────────────────
def get_national_agg(df):
    """Agregat nasional per tahun."""
    agg_dict = {
        'rata_rr': ('RR', 'mean'),
        'total_phk': ('PHK', 'sum'),
        'rata_phk': ('PHK', 'mean'),
    }
    if 'TPAK' in df.columns:
        agg_dict['rata_tpak'] = ('TPAK', 'mean')
    if 'IPM' in df.columns:
        agg_dict['rata_ipm'] = ('IPM', 'mean')

    agg = df.groupby('Tahun').agg(**agg_dict).reset_index()
    return agg


def get_rr_status(rr_val):
    """Klasifikasikan RR."""
    if rr_val > 1.5:
        return 'Risiko Tinggi'
    elif rr_val > 1.0:
        return 'Di atas Rata-rata'
    elif rr_val > 0.75:
        return 'Di bawah Rata-rata'
    else:
        return 'Rendah'
