"""
tbc_data.py — Data loader untuk Dashboard TBC Indonesia
Membaca dari CSV yang di-export dari model INLA.
"""
import os
import pandas as pd
import numpy as np

_DIR = os.path.dirname(__file__)

# ── Load data utama ──────────────────────────────────────────────────────────
def load_tbc_data():
    """Load data TBC per provinsi per tahun (204 baris: 34 prov × 6 tahun)."""
    df = pd.read_csv(os.path.join(_DIR, 'tbc_data.csv'), encoding='utf-8')
    df['Tahun'] = df['Tahun'].astype(int)
    return df

def load_fixed_effects():
    """Load hasil estimasi fixed effects (kovariat) model INLA."""
    return pd.read_csv(os.path.join(_DIR, 'fixed_effects.csv'), encoding='utf-8')

def load_hyperparameter():
    """Load posterior hyperparameter model."""
    return pd.read_csv(os.path.join(_DIR, 'hyperparameter.csv'), encoding='utf-8')

def load_diagnostik():
    """Load diagnostik model (DIC, WAIC, CPO)."""
    return pd.read_csv(os.path.join(_DIR, 'diagnostik.csv'), encoding='utf-8')

def load_temporal():
    """Load efek random temporal RW1."""
    return pd.read_csv(os.path.join(_DIR, 'temporal.csv'), encoding='utf-8')

def load_efek_spasial():
    """Load efek random spasial Leroux per provinsi."""
    return pd.read_csv(os.path.join(_DIR, 'efek_spasial.csv'), encoding='utf-8')

def load_rr_provinsi():
    """Load rata-rata RR per provinsi (agregat 2020-2025)."""
    return pd.read_csv(os.path.join(_DIR, 'rr_provinsi.csv'), encoding='utf-8')


# ── Mapping ──────────────────────────────────────────────────────────────────
# Provinsi → Pulau (untuk grouping chart)
PROVINSI_PULAU = {
    'Aceh': 'Sumatera', 'Sumatera Utara': 'Sumatera', 'Sumatera Barat': 'Sumatera',
    'Riau': 'Sumatera', 'Jambi': 'Sumatera', 'Sumatera Selatan': 'Sumatera',
    'Bengkulu': 'Sumatera', 'Lampung': 'Sumatera',
    'Kepulauan Bangka Belitung': 'Sumatera', 'Kepulauan Riau': 'Sumatera',
    'DKI Jakarta': 'Jawa', 'Jawa Barat': 'Jawa', 'Jawa Tengah': 'Jawa',
    'DI Yogyakarta': 'Jawa', 'Jawa Timur': 'Jawa', 'Banten': 'Jawa',
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
    'accent_teal'   : '#2a7c8c',
    'accent_blue'   : '#3b7dbf',
    'accent_green'  : '#2e8b57',
    'accent_amber'  : '#c0775a',
    'danger'        : '#d94f4f',
    'success'       : '#2e8b57',
    'warning'       : '#c0775a',
    'text_primary'  : '#1e293b',
    'text_secondary': '#475569',
    'text_muted'    : '#94a3b8',
    # Viridis-inspired, matches R maps
    'chart_sequence': ['#3d8b8a', '#5ba4a4', '#7ab8b8', '#4a8fa8',
                       '#7caec4', '#9fc5d5', '#b8d4e3', '#80cbc4',
                       '#26a69a', '#1e3a4f'],
    'viridis': ['#440154', '#31688e', '#35b779', '#fde725'],
}

# ── Computed aggregates ───────────────────────────────────────────────────────
def get_national_agg(df):
    """Agregat nasional per tahun."""
    agg = df.groupby('Tahun').agg(
        rata_rate=('Rate_per100k', 'mean'),
        rata_rr  =('RR', 'mean'),
        total_y  =('Y', 'sum'),
        rata_sanitasi  =('Sanitasi', 'mean'),
        rata_airminum  =('AirMinum', 'mean'),
        rata_lamaSekolah=('LamaSekolah', 'mean'),
        rata_rumahLayak =('RumahLayak', 'mean'),
    ).reset_index()
    return agg

def get_rr_status(rr_val):
    """Klasifikasikan RR."""
    if rr_val > 1.5:
        return 'Sangat Tinggi'
    elif rr_val > 1.0:
        return 'Di atas Rata-rata'
    elif rr_val > 0.75:
        return 'Di bawah Rata-rata'
    else:
        return 'Rendah'
