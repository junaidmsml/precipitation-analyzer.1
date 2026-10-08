import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_CENTER

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Precipitation Analyzer",
    page_icon="🌧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# THEME STATE
# ─────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌧 Precipitation Analyzer")
    st.caption("Analyze • Visualize • Understand")
    st.divider()

    st.markdown("#### 📁 Upload Dataset")
    uploaded_file = st.file_uploader(
        "Drop CSV / Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload a file with date and rainfall columns.",
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown("#### ⚙️ Settings")

    theme_choice = st.radio(
        "Theme",
        ["🌙 Dark", "☀️ Light"],
        index=0,
        horizontal=True,
        help="Dashboard theme.",
    )
    st.session_state.theme = "dark" if "Dark" in theme_choice else "light"

    st.divider()
    st.markdown("#### 📊 Sections")
    show_stats = st.checkbox("Statistics", value=True)
    show_timeseries = st.checkbox("Time Series", value=True)
    show_cumulative = st.checkbox("Cumulative", value=True)
    show_extremes = st.checkbox("Extremes", value=True)
    show_anomaly = st.checkbox("Anomaly", value=True)

    st.divider()
    st.caption("**by Junaid Ali**")
    st.caption("Civil Engineering Research")

# ─────────────────────────────────────────────
# COLOR PALETTES
# ─────────────────────────────────────────────
PALETTES = {
    "dark": {
        "bg": (
            "radial-gradient(circle at 12% 8%, rgba(56,189,248,0.20), transparent 42%),"
            "radial-gradient(circle at 88% 18%, rgba(167,139,250,0.20), transparent 46%),"
            "linear-gradient(160deg, #070B14 0%, #0B1220 50%, #111A2E 100%)"
        ),
        "sidebar-bg": "linear-gradient(180deg, #0E1730 0%, #0A1020 100%)",
        "card": "rgba(19, 28, 46, 0.75)",
        "card-border": "rgba(56,189,248,0.20)",
        "text": "#E2E8F0",
        "muted": "#94A3B8",
        "subtle": "#64748B",
        "accent": "#38BDF8",
        "accent2": "#A78BFA",
        "glow": "rgba(56,189,248,0.38)",
        "shadow": "rgba(0,0,0,0.45)",
        "input-bg": "rgba(15,23,42,0.85)",
        "popup-bg": "#0B1220",
        "line": "rgba(148,163,184,0.15)",
        "title-grad": "linear-gradient(90deg, #38BDF8, #A78BFA)",
    },
    "light": {
        "bg": (
            "radial-gradient(circle at 10% 0%, rgba(14,165,233,0.20), transparent 45%),"
            "radial-gradient(circle at 90% 10%, rgba(139,92,246,0.15), transparent 45%),"
            "linear-gradient(160deg, #F0F9FF 0%, #EEF2FF 60%, #F8FAFC 100%)"
        ),
        "sidebar-bg": "linear-gradient(180deg, #E0F2FE 0%, #EDE9FE 100%)",
        "card": "rgba(255, 255, 255, 0.85)",
        "card-border": "rgba(2,132,199,0.25)",
        "text": "#0F172A",
        "muted": "#475569",
        "subtle": "#64748B",
        "accent": "#0284C7",
        "accent2": "#7C3AED",
        "glow": "rgba(2,132,199,0.30)",
        "shadow": "rgba(15,23,42,0.14)",
        "input-bg": "#FFFFFF",
        "popup-bg": "#FFFFFF",
        "line": "rgba(15,23,42,0.10)",
        "title-grad": "linear-gradient(90deg, #0284C7, #7C3AED)",
    },
}

P = PALETTES[st.session_state.theme]
ROOT_VARS = ":root{" + "".join(f"--{k}:{v};" for k, v in P.items()) + "}"

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
STATIC_CSS = """
html, body, [class*="css"], .stApp, .stMarkdown, .stText,
button, input, select, textarea, label, p, h1, h2, h3, h4, h5, h6 {
    font-family: 'Times New Roman', Times, serif !important;
}
.stApp {
    background: var(--bg) !important;
    background-attachment: fixed !important;
    color: var(--text);
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid var(--line);
}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
.stCheckbox label p, .stRadio label p {
    color: var(--text);
}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p { color: var(--muted) !important; }
hr { border-color: var(--line) !important; }

div[data-baseweb="select"] > div {
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--card-border) !important;
}
div[data-baseweb="select"] span, div[data-baseweb="select"] svg { color: var(--text) !important; fill: var(--text) !important; }
[data-testid="stFileUploaderDropzone"] {
    background: var(--input-bg) !important;
    border: 1px dashed var(--accent) !important;
    border-radius: 10px;
}
[data-testid="stFileUploaderDropzone"] * { color: var(--text) !important; }
[data-testid="stFileUploaderDropzone"] small { color: var(--muted) !important; }
button[kind], .stButton > button {
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--card-border) !important;
}

[data-testid="stFileUploaderDropzone"],
div[data-baseweb="select"],
[data-testid="stCheckbox"],
[data-testid="stRadio"],
[data-testid="stAlert"],
[data-testid="stDataFrame"],
button,
.empty-box, .metric-card, .main-header, .section-title {
    transition: transform 0.25s cubic-bezier(.2,.8,.2,1),
                box-shadow 0.25s ease,
                border-color 0.25s ease,
                background 0.25s ease;
}
[data-testid="stFileUploaderDropzone"]:hover,
div[data-baseweb="select"]:hover {
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 10px 24px var(--shadow), 0 0 0 1px var(--accent), 0 0 18px var(--glow);
}
[data-testid="stCheckbox"]:hover,
[data-testid="stRadio"]:hover {
    transform: translateX(6px) scale(1.03);
    filter: drop-shadow(0 4px 10px var(--glow));
}
button:hover {
    transform: translateY(-3px) scale(1.06);
    box-shadow: 0 10px 22px var(--shadow), 0 0 16px var(--glow);
    border-color: var(--accent) !important;
}
[data-testid="stAlert"]:hover,
[data-testid="stDataFrame"]:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 14px 30px var(--shadow), 0 0 22px var(--glow);
}

.main-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.8rem 1.2rem;
    border: 1px solid var(--card-border);
    border-radius: 12px;
    background: var(--card);
    backdrop-filter: blur(8px);
}
.main-header:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 14px 30px var(--shadow), 0 0 24px var(--glow);
}
.main-header .main-title {
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    background: var(--title-grad);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
}
.main-header .main-subtitle {
    font-size: 0.9rem;
    color: var(--muted);
    margin: 0;
    font-style: italic;
}
.main-header .author-tag {
    font-size: 0.95rem;
    color: var(--muted);
    font-style: italic;
}

.metric-card {
    background: var(--card);
    border: 1px solid var(--card-border);
    border-left: 4px solid var(--accent);
    padding: 1rem 1.1rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px var(--shadow);
    backdrop-filter: blur(8px);
}
.metric-card:hover {
    transform: translateY(-8px) scale(1.05);
    border-left-color: var(--accent2);
    box-shadow: 0 18px 36px var(--shadow), 0 0 28px var(--glow);
}
.metric-card .metric-label {
    font-size: 0.78rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.6px;
}
.metric-card .metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    margin-top: 0.25rem;
}

.info-icon {
    display: inline-block;
    margin-left: 6px;
    color: var(--accent);
    cursor: help;
    font-size: 0.9rem;
    position: relative;
}
.info-icon:hover { transform: scale(1.35); }
.info-icon .popup {
    visibility: hidden;
    opacity: 0;
    width: 280px;
    background: var(--popup-bg);
    color: var(--text);
    border: 1px solid var(--accent);
    border-radius: 10px;
    padding: 10px 12px;
    position: absolute;
    z-index: 9999;
    bottom: 130%;
    left: 50%;
    margin-left: -140px;
    transition: opacity 0.2s ease;
    font-size: 0.85rem;
    line-height: 1.4;
}
.info-icon:hover .popup {
    visibility: visible;
    opacity: 1;
}
.popup-title {
    font-weight: 700;
    color: var(--accent);
    display: block;
    margin-bottom: 4px;
}

[data-testid="stTooltipContent"] {
    background: var(--popup-bg) !important;
    color: var(--text) !important;
    border: 1px solid var(--accent) !important;
    border-radius: 10px !important;
}

.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text);
    margin: 1.6rem 0 0.7rem 0;
    padding-bottom: 0.35rem;
    border-bottom: 2px solid var(--line);
}
.section-title:hover {
    transform: translateX(8px);
    border-bottom-color: var(--accent);
    color: var(--accent);
}

.empty-box {
    border: 2px dashed var(--accent);
    border-radius: 14px;
    padding: 3rem 2rem;
    text-align: center;
    background: var(--card);
    backdrop-filter: blur(8px);
    margin-top: 1rem;
}
.empty-box:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 20px 40px var(--shadow), 0 0 34px var(--glow);
    border-color: var(--accent2);
}
.empty-box h3 { color: var(--text); margin: 0; }
.empty-box p { color: var(--muted); margin-top: 0.5rem; }
.empty-box small { color: var(--subtle); font-size: 0.85rem; }

.footer {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid var(--line);
    text-align: center;
    font-size: 0.85rem;
    color: var(--subtle);
    font-style: italic;
}
"""

st.markdown(f"<style>{ROOT_VARS}{STATIC_CSS}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div>
        <p class="main-title">🌧 Precipitation Analyzer</p>
        <p class="main-subtitle">Analyze • Visualize • Understand</p>
    </div>
    <div class="author-tag">by Junaid Ali</div>
</div>
""", unsafe_allow_html=True)

st.write("")

# ─────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────
if uploaded_file is None:
    st.markdown("""
    <div class="empty-box">
        <h3>📁 Drop CSV / Excel file here</h3>
        <p>or use the sidebar to browse</p>
        <small>Supported: .csv, .xlsx, .xls</small>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown('<p class="section-title">ℹ️ What happens next?</p>', unsafe_allow_html=True)
    st.markdown("""
    - Automatic column detection (date + rainfall)
    - Data quality check
    - Full statistical analysis + charts
    - Downloadable professional PDF report
    """)

    st.markdown("""
    <div class="footer">
        Developed by Junaid Ali · Civil Engineering Research
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
try:
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"❌ Could not read file: {e}")
    st.stop()

st.success(f"✅ Loaded **{uploaded_file.name}** — {len(df):,} rows × {len(df.columns)} columns")

st.write("")
st.markdown('<p class="section-title">👀 Data Preview</p>', unsafe_allow_html=True)
st.dataframe(df.head(10), use_container_width=True)

# ─────────────────────────────────────────────
# DATA SUMMARY
# ─────────────────────────────────────────────
st.write("")
st.markdown('<p class="section-title">📊 Data Summary</p>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Records</div><div class="metric-value">{len(df):,}</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card"><div class="metric-label">Columns</div><div class="metric-value">{len(df.columns)}</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""<div class="metric-card"><div class="metric-label">Status</div><div class="metric-value">Loaded</div></div>""", unsafe_allow_html=True)
with c4:
    st.markdown("""<div class="metric-card"><div class="metric-label">Engine</div><div class="metric-value">V2</div></div>""", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# AUTO-DETECT DATE & RAINFALL COLUMNS
# ═════════════════════════════════════════════
def detect_columns(df):
    date_col, rain_col = None, None
    date_names = ["date", "datetime", "time", "timestamp", "day", "dt"]
    rain_names = ["rainfall", "rain", "precipitation", "precip", "prcp", "p"]
    for c in df.columns:
        if str(c).lower() in date_names:
            date_col = c
            break
    for c in df.columns:
        if str(c).lower() in rain_names:
            rain_col = c
            break
    if date_col is None:
        for c in df.columns:
            try:
                pd.to_datetime(df[c].head(20), errors="raise")
                date_col = c
                break
            except Exception:
                continue
    if rain_col is None:
        for c in df.columns:
            if pd.api.types.is_numeric_dtype(df[c]) and c != date_col:
                rain_col = c
                break
    return date_col, rain_col


date_col, rain_col = detect_columns(df)

if date_col is None or rain_col is None:
    st.error("❌ Could not auto-detect **date** or **rainfall** column.")
    st.stop()

st.success(f"✅ Detected — **Date:** `{date_col}` | **Rainfall:** `{rain_col}`")

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
df[rain_col] = pd.to_numeric(df[rain_col], errors="coerce")
df = df.dropna(subset=[date_col]).sort_values(date_col).reset_index(drop=True)

working = df[[date_col, rain_col]].copy()
working.columns = ["date", "rainfall"]
working["rainfall"] = working["rainfall"].fillna(0)

# ═════════════════════════════════════════════
# CORE VALUES (always computed, also used by PDF report)
# ═════════════════════════════════════════════
r = working["rainfall"]
stats = {
    "Total": float(r.sum()),
    "Mean": float(r.mean()),
    "Median": float(r.median()),
    "Std Dev": float(r.std()) if len(r) > 1 else 0,
    "Maximum": float(r.max()),
    "Minimum": float(r.min()),
    "Rainy Days": int((r > 0).sum()),
    "Zero Days": int((r == 0).sum()),
}

deltas = working["date"].diff().dropna().dt.days
if len(deltas):
    mode_delta = deltas.mode().iloc[0] if len(deltas.mode()) else 1
    resolution = {1: "Daily", 7: "Weekly", 30: "Monthly", 365: "Annual"}.get(
        int(mode_delta), f"{int(mode_delta)}-day"
    )
else:
    resolution = "N/A"

# ═════════════════════════════════════════════
# DATA QUALITY
# ═════════════════════════════════════════════
if show_stats:
    st.write("")
    st.markdown('<p class="section-title">🧪 Data Quality</p>', unsafe_allow_html=True)
    total = len(working)
    date_min, date_max = working["date"].min(), working["date"].max()
    expected_days = (date_max - date_min).days + 1
    missing_dates = expected_days - total
    duplicates = working["date"].duplicated().sum()

    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Date Range</div><div class="metric-value" style="font-size:1rem;">{date_min.strftime('%Y-%m-%d')} → {date_max.strftime('%Y-%m-%d')}</div></div>""", unsafe_allow_html=True)
    with q2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Missing Dates</div><div class="metric-value">{missing_dates:,}</div></div>""", unsafe_allow_html=True)
    with q3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Duplicates</div><div class="metric-value">{duplicates:,}</div></div>""", unsafe_allow_html=True)
    with q4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Resolution</div><div class="metric-value">{resolution}</div></div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════
# BASIC STATISTICS
# ═════════════════════════════════════════════
if show_stats:
    st.write("")
    st.markdown('<p class="section-title">📊 Basic Statistics</p>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Rainfall</div><div class="metric-value">{stats['Total']:.1f} mm</div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Mean</div><div class="metric-value">{stats['Mean']:.2f} mm</div></div>""", unsafe_allow_html=True)
    with s3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Median</div><div class="metric-value">{stats['Median']:.2f} mm</div></div>""", unsafe_allow_html=True)
    with s4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Std Dev</div><div class="metric-value">{stats['Std Dev']:.2f} mm</div></div>""", unsafe_allow_html=True)

    s5, s6, s7, s8 = st.columns(4)
    with s5:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Maximum</div><div class="metric-value">{stats['Maximum']:.1f} mm</div></div>""", unsafe_allow_html=True)
    with s6:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Minimum</div><div class="metric-value">{stats['Minimum']:.1f} mm</div></div>""", unsafe_allow_html=True)
    with s7:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Rainy Days</div><div class="metric-value">{stats['Rainy Days']:,}</div></div>""", unsafe_allow_html=True)
    with s8:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Zero Days</div><div class="metric-value">{stats['Zero Days']:,}</div></div>""", unsafe_allow_html=True)


# Chart styling
def style_fig(fig, title):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Times New Roman", size=18, color=P["text"])),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Times New Roman", size=12, color=P["text"]),
        margin=dict(l=40, r=20, t=60, b=40),
        xaxis=dict(gridcolor=P["line"]),
        yaxis=dict(gridcolor=P["line"]),
    )
    return fig


# ═════════════════════════════════════════════
# TIME SERIES
# ═════════════════════════════════════════════
if show_timeseries:
    st.write("")
    st.markdown('<p class="section-title">📈 Precipitation Time Series</p>', unsafe_allow_html=True)

    fig_daily = go.Figure()
    fig_daily.add_trace(go.Scatter(
        x=working["date"], y=working["rainfall"],
        mode="lines", line=dict(color=P["accent"], width=1),
        fill="tozeroy", fillcolor="rgba(56,189,248,0.15)", name="Daily"
    ))
    fig_daily = style_fig(fig_daily, "Daily Precipitation")
    st.plotly_chart(fig_daily, use_container_width=True)

    monthly = working.set_index("date")["rainfall"].resample("ME").sum().reset_index()
    monthly.columns = ["month", "rainfall"]
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(x=monthly["month"], y=monthly["rainfall"], marker=dict(color=P["accent2"])))
    fig_monthly = style_fig(fig_monthly, "Monthly Precipitation Totals")
    st.plotly_chart(fig_monthly, use_container_width=True)

    annual = working.set_index("date")["rainfall"].resample("YE").sum().reset_index()
    annual["year"] = annual["date"].dt.year
    fig_annual = go.Figure()
    fig_annual.add_trace(go.Bar(x=annual["year"].astype(str), y=annual["rainfall"], marker=dict(color=P["accent"])))
    fig_annual = style_fig(fig_annual, "Annual Precipitation Totals")
    st.plotly_chart(fig_annual, use_container_width=True)

    working["month"] = working["date"].dt.month
    clim = working.groupby("month")["rainfall"].mean().reset_index()
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    fig_clim = go.Figure()
    fig_clim.add_trace(go.Bar(x=[month_names[m - 1] for m in clim["month"]], y=clim["rainfall"], marker=dict(color=P["accent2"])))
    fig_clim = style_fig(fig_clim, "Monthly Climatology (Average)")
    st.plotly_chart(fig_clim, use_container_width=True)

# ═════════════════════════════════════════════
# CUMULATIVE
# ═════════════════════════════════════════════
if show_cumulative:
    st.write("")
    st.markdown('<p class="section-title">📉 Cumulative Rainfall (Mass Curve)</p>', unsafe_allow_html=True)
    working["cumulative"] = working["rainfall"].cumsum()
    fig_cum = go.Figure()
    fig_cum.add_trace(go.Scatter(
        x=working["date"], y=working["cumulative"],
        mode="lines", line=dict(color=P["accent2"], width=2), name="Cumulative"
    ))
    fig_cum = style_fig(fig_cum, "Cumulative Rainfall Mass Curve")
    st.plotly_chart(fig_cum, use_container_width=True)

# ═════════════════════════════════════════════
# EXTREMES
# ═════════════════════════════════════════════
if show_extremes:
    st.write("")
    st.markdown('<p class="section-title">🔥 Extreme Rainfall Events</p>', unsafe_allow_html=True)
    top10 = working.nlargest(10, "rainfall")[["date", "rainfall"]].reset_index(drop=True)
    top10.index += 1
    top10["date"] = top10["date"].dt.strftime("%Y-%m-%d")
    st.dataframe(top10.rename(columns={"date": "Date", "rainfall": "Rainfall (mm)"}), use_container_width=True)

    max_row = working.loc[working["rainfall"].idxmax()]
    e1, e2 = st.columns(2)
    with e1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Maximum Event</div><div class="metric-value">{max_row['rainfall']:.1f} mm</div></div>""", unsafe_allow_html=True)
    with e2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Date of Maximum</div><div class="metric-value">{max_row['date'].strftime('%Y-%m-%d')}</div></div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════
# ANOMALY
# ═════════════════════════════════════════════
if show_anomaly:
    st.write("")
    st.markdown('<p class="section-title">📊 Anomaly Analysis</p>', unsafe_allow_html=True)

    working["year"] = working["date"].dt.year
    years = sorted(working["year"].unique())
    if len(years) >= 2:
        b1, b2 = st.columns(2)
        with b1:
            base_start = st.selectbox("Baseline start year", years, index=0)
        with b2:
            base_end = st.selectbox("Baseline end year", years, index=min(2, len(years) - 1))

        baseline = working[(working["year"] >= base_start) & (working["year"] <= base_end)]
        baseline_mean = baseline["rainfall"].mean()

        monthly_anom = working.set_index("date")["rainfall"].resample("ME").sum().reset_index()
        monthly_anom.columns = ["month", "rainfall"]
        monthly_anom["anomaly"] = monthly_anom["rainfall"] - baseline_mean * 30

        colors_anom = [P["accent"] if a >= 0 else "#EF4444" for a in monthly_anom["anomaly"]]
        fig_anom = go.Figure()
        fig_anom.add_trace(go.Bar(x=monthly_anom["month"], y=monthly_anom["anomaly"], marker=dict(color=colors_anom)))
        fig_anom.add_hline(y=0, line=dict(color=P["muted"], width=1, dash="dash"))
        fig_anom = style_fig(fig_anom, f"Monthly Anomaly (Baseline {base_start}–{base_end})")
        st.plotly_chart(fig_anom, use_container_width=True)
    else:
        st.info("ℹ️ Anomaly analysis requires at least 2 years of data.")

# ═════════════════════════════════════════════
# DOWNLOADS
# ═════════════════════════════════════════════
st.write("")
st.markdown('<p class="section-title">📥 Export</p>', unsafe_allow_html=True)

d1, d2 = st.columns(2)

with d1:
    csv_data = working[["date", "rainfall"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        "📊 Download Cleaned CSV",
        data=csv_data,
        file_name="cleaned_rainfall.csv",
        mime="text/csv",
        use_container_width=True,
    )

with d2:
    if st.button("📄 Generate PDF Report", use_container_width=True):
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            elements = []
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle("T", parent=styles["Title"], fontName="Times-Bold", fontSize=20, textColor=colors.HexColor("#0284C7"), alignment=TA_CENTER)
            h_style = ParagraphStyle("H", parent=styles["Heading2"], fontName="Times-Bold", fontSize=14, textColor=colors.HexColor("#0284C7"))

            elements.append(Paragraph("Precipitation Analysis Report", title_style))
            elements.append(Spacer(1, 0.3 * inch))
            elements.append(Paragraph("1. Dataset Information", h_style))
            info_data = [
                ["File", uploaded_file.name],
                ["Records", f"{len(working):,}"],
                ["Date Range", f"{working['date'].min().strftime('%Y-%m-%d')} to {working['date'].max().strftime('%Y-%m-%d')}"],
                ["Resolution", resolution],
            ]
            t = Table(info_data, colWidths=[1.8 * inch, 4.5 * inch])
            t.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "Times-Roman"), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
            elements.append(t)
            elements.append(Spacer(1, 0.3 * inch))

            elements.append(Paragraph("2. Statistics", h_style))
            stat_data = [[k, f"{v:.2f}"] for k, v in stats.items()]
            t2 = Table(stat_data, colWidths=[2.5 * inch, 3.8 * inch])
            t2.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "Times-Roman"), ("GRID", (0, 0), (-1, -1), 0.5, colors.grey)]))
            elements.append(t2)

            doc.build(elements)
            buffer.seek(0)
            st.download_button(
                "⬇️ Download PDF",
                data=buffer,
                file_name="precipitation_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"PDF error: {e}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Developed by Junaid Ali · Civil Engineering Research
</div>
""", unsafe_allow_html=True)
