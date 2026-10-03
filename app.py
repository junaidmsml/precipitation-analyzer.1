import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
# CUSTOM CSS — Times New Roman + Scientific Look
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ─── GLOBAL FONT: Times New Roman ─── */
    html, body, [class*="css"], .stApp, .stMarkdown, .stText,
    button, input, select, textarea, label, p, h1, h2, h3, h4, h5, h6 {
        font-family: 'Times New Roman', Times, serif !important;
    }

    /* ─── HEADER ─── */
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0 0.4rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }
    .main-title {
        font-size: 1.7rem;
        font-weight: 700;
        color: #E5E7EB;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .main-subtitle {
        font-size: 0.9rem;
        color: #9CA3AF;
        margin: 0;
        font-style: italic;
    }
    .author-tag {
        font-size: 0.95rem;
        color: #9CA3AF;
        font-style: italic;
    }

    /* ─── METRIC CARDS ─── */
    .metric-card {
        background: #1A1D24;
        border-left: 3px solid #3B82F6;
        padding: 1rem 1.1rem;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        position: relative;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #9CA3AF;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .metric-value {
        font-size: 1.45rem;
        font-weight: 600;
        color: #E5E7EB;
        margin-top: 0.25rem;
    }

    /* ─── CUSTOM HOVER POPUP (ⓘ) ─── */
    .info-icon {
        display: inline-block;
        margin-left: 6px;
        color: #3B82F6;
        cursor: help;
        font-size: 0.85rem;
        position: relative;
    }
    .info-icon .popup {
        visibility: hidden;
        opacity: 0;
        width: 280px;
        background: #0E1117;
        color: #E5E7EB;
        text-align: left;
        border: 1px solid #3B82F6;
        border-radius: 6px;
        padding: 10px 12px;
        position: absolute;
        z-index: 9999;
        bottom: 130%;
        left: 50%;
        margin-left: -140px;
        transition: opacity 0.2s ease;
        font-size: 0.82rem;
        line-height: 1.35;
        box-shadow: 0 4px 14px rgba(0,0,0,0.5);
    }
    .info-icon:hover .popup {
        visibility: visible;
        opacity: 1;
    }
    .popup-title {
        font-weight: 700;
        color: #60A5FA;
        display: block;
        margin-bottom: 4px;
        font-size: 0.88rem;
    }
    .popup-formula {
        display: block;
        margin-top: 6px;
        padding-top: 6px;
        border-top: 1px solid rgba(255,255,255,0.1);
        color: #93C5FD;
        font-style: italic;
        font-size: 0.8rem;
    }

    /* ─── SECTION TITLE ─── */
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #E5E7EB;
        margin: 1.6rem 0 0.7rem 0;
        padding-bottom: 0.35rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        letter-spacing: 0.3px;
    }

    /* ─── FOOTER ─── */
    .footer {
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.08);
        text-align: center;
        font-size: 0.85rem;
        color: #6B7280;
        font-style: italic;
    }

    /* ─── EMPTY STATE BOX ─── */
    .empty-box {
        border: 2px dashed #374151;
        border-radius: 10px;
        padding: 3rem 2rem;
        text-align: center;
        background: #1A1D24;
        margin-top: 1rem;
    }
    .empty-box h3 {
        color: #E5E7EB;
        margin: 0;
    }
    .empty-box p {
        color: #9CA3AF;
        margin-top: 0.5rem;
    }
    .empty-box small {
        color: #6B7280;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

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
        help="Dashboard theme. Dark is default.",
    )
    st.session_state.theme = "dark" if "Dark" in theme_choice else "light"

    baseline_year = st.selectbox(
        "Baseline period (for anomaly)",
        ["None", "2018–2020", "2019–2021", "2020–2022"],
        help="Reference period used to compute precipitation anomalies.",
    )

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
    if uploaded_file.name.endswith(".csv"):
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
# DATA SUMMARY (with custom hover popups)
# ─────────────────────────────────────────────
st.write("")
st.markdown('<p class="section-title">📊 Data Summary</p>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">
            Records
            <span class="info-icon">ⓘ
                <span class="popup">
                    <span class="popup-title">Records</span>
                    Total number of rows in the uploaded dataset.
                </span>
            </span>
        </div>
        <div class="metric-value">{len(df):,}</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">
            Columns
            <span class="info-icon">ⓘ
                <span class="popup">
                    <span class="popup-title">Columns</span>
                    Number of variables detected in the file.
                </span>
            </span>
        </div>
        <div class="metric-value">{len(df.columns)}</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">
            Status
            <span class="info-icon">ⓘ
                <span class="popup">
                    <span class="popup-title">Status</span>
                    Current state of the loaded dataset.
                </span>
            </span>
        </div>
        <div class="metric-value">Loaded</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">
            Engine
            <span class="info-icon">ⓘ
                <span class="popup">
                    <span class="popup-title">Analysis Engine</span>
                    Core version of the precipitation analyzer.
                </span>
            </span>
        </div>
        <div class="metric-value">V1</div>
    </div>
    """, unsafe_allow_html=True)

st.info("🔧 **Step 1 complete.** Next: auto-detect date & rainfall columns, then full statistics, charts, and PDF report.")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Developed by Junaid Ali · Civil Engineering Research
</div>
""", unsafe_allow_html=True)