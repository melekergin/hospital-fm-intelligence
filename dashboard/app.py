import streamlit as st
import duckdb
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hospital FM Intelligence Hub",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    /* Dark gradient background */
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #0d1528 50%, #0a1020 100%);
        color: #e2e8f0;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1528 0%, #111827 100%);
        border-right: 1px solid rgba(99,179,237,0.15);
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(99,179,237,0.2);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        backdrop-filter: blur(8px);
    }
    [data-testid="stMetricLabel"] { color: #94a3b8; font-size: 0.78rem; font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase; }
    [data-testid="stMetricValue"] { color: #e2e8f0; font-size: 1.6rem; font-weight: 700; }
    [data-testid="stMetricDelta"] svg { display: none; }

    /* Section headers */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #63b3ed;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid rgba(99,179,237,0.2);
        margin: 1.5rem 0 1rem 0;
    }

    /* Risk band badges */
    .badge-high        { background:#7f1d1d; color:#fca5a5; border: 1px solid #ef4444; border-radius:6px; padding:2px 10px; font-weight:600; font-size:0.8rem; }
    .badge-significant { background:#78350f; color:#fcd34d; border: 1px solid #f59e0b; border-radius:6px; padding:2px 10px; font-weight:600; font-size:0.8rem; }
    .badge-moderate    { background:#1e3a5f; color:#93c5fd; border: 1px solid #3b82f6; border-radius:6px; padding:2px 10px; font-weight:600; font-size:0.8rem; }
    .badge-low         { background:#14532d; color:#86efac; border: 1px solid #22c55e; border-radius:6px; padding:2px 10px; font-weight:600; font-size:0.8rem; }

    /* Dataframe */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

    /* Title */
    .main-title { font-size: 2rem; font-weight: 700; color: #e2e8f0; }
    .main-subtitle { color: #64748b; font-size: 0.95rem; margin-top: -0.5rem; }

    div[data-testid="stHorizontalBlock"] { gap: 1rem; }
</style>
""", unsafe_allow_html=True)

# ── DB connection ─────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'hospital_fm.db')

@st.cache_resource
def get_conn():
    return duckdb.connect(DB_PATH, read_only=True)

@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    return get_conn().execute(sql).fetchdf()

# ── Load data ─────────────────────────────────────────────────────────────────
summary    = query("SELECT * FROM kpi_trust_summary ORDER BY backlog_gbp DESC")
risk       = query("SELECT * FROM kpi_backlog_risk_band ORDER BY year_sort, risk_rank")
trend      = query("SELECT * FROM kpi_maintenance_backlog_trend ORDER BY trust_code, year_sort")
energy     = query("SELECT * FROM kpi_energy_cost_per_bed ORDER BY trust_code, year_sort")
backlog_pt = query("SELECT * FROM kpi_maintenance_backlog_per_trust ORDER BY year, trust_code")

all_trusts = sorted(summary['trust_code'].tolist())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏥 FM Intelligence Hub")
    st.markdown("---")
    st.markdown("**Filters**")
    selected_trusts = st.multiselect(
        "Trust(s)",
        options=all_trusts,
        default=all_trusts,
        help="Filter all charts to specific trusts"
    )
    st.markdown("---")
    st.markdown("**Data source**")
    st.caption("NHS ERIC · DuckDB · Bruin")
    st.caption("Refreshes every 5 min")

# ── Filter ────────────────────────────────────────────────────────────────────
if selected_trusts:
    summary    = summary[summary['trust_code'].isin(selected_trusts)]
    risk       = risk[risk['trust_code'].isin(selected_trusts)]
    trend      = trend[trend['trust_code'].isin(selected_trusts)]
    energy     = energy[energy['trust_code'].isin(selected_trusts)]
    backlog_pt = backlog_pt[backlog_pt['trust_code'].isin(selected_trusts)]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">🏥 Hospital FM Intelligence Hub</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">NHS Estates Returns Information Collection (ERIC) · Facilities Management KPIs</p>', unsafe_allow_html=True)
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Executive Summary — Latest Year</p>', unsafe_allow_html=True)

total_backlog   = summary['backlog_gbp'].sum()
total_energy    = summary['energy_cost_gbp'].sum()
total_beds      = summary['available_beds'].sum()
avg_ecpb        = summary['energy_cost_per_bed'].mean()
avg_bcpb        = summary['backlog_cost_per_bed'].mean()
n_trusts        = len(summary)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Trusts Tracked",         f"{n_trusts}")
c2.metric("Total Backlog",          f"£{total_backlog/1e6:.1f}M")
c3.metric("Total Energy Cost",      f"£{total_energy/1e6:.1f}M")
c4.metric("Avg Energy / Bed",       f"£{avg_ecpb:,.0f}")
c5.metric("Avg Backlog / Bed",      f"£{avg_bcpb:,.0f}")

st.markdown("---")

# ── Row 1: Backlog by trust (bar) + Risk Band table ───────────────────────────
st.markdown('<p class="section-header">Maintenance Backlog Overview</p>', unsafe_allow_html=True)

col_left, col_right = st.columns([3, 2])

with col_left:
    fig_bar = px.bar(
        summary.sort_values('backlog_gbp', ascending=True),
        x='backlog_gbp', y='trust_code',
        orientation='h',
        color='backlog_change_pct',
        color_continuous_scale=['#22c55e', '#eab308', '#ef4444'],
        color_continuous_midpoint=0,
        labels={'backlog_gbp': 'Backlog (£)', 'trust_code': 'Trust', 'backlog_change_pct': 'YoY Change %'},
        title='Total Maintenance Backlog (£) — Latest Year',
        text=summary.sort_values('backlog_gbp', ascending=True)['backlog_gbp'].apply(lambda x: f"£{x/1e6:.2f}M"),
    )
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        title_font=dict(size=14, color='#94a3b8'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', color='#64748b'),
        yaxis=dict(showgrid=False, color='#94a3b8'),
        coloraxis_colorbar=dict(title=dict(text='YoY %', font=dict(color='#94a3b8')), tickfont=dict(color='#94a3b8')),
        margin=dict(l=20, r=20, t=40, b=20),
        height=320,
    )
    fig_bar.update_traces(textposition='outside', textfont=dict(color='#e2e8f0', size=11))
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.markdown("**Risk Band — Latest Year**")
    latest_risk = risk[risk['year_sort'] == risk['year_sort'].max()].copy()

    BAND_MAP = {
        'HIGH':        '<span class="badge-high">HIGH</span>',
        'SIGNIFICANT': '<span class="badge-significant">SIGNIFICANT</span>',
        'MODERATE':    '<span class="badge-moderate">MODERATE</span>',
        'LOW':         '<span class="badge-low">LOW</span>',
    }

    for _, row in latest_risk.iterrows():
        badge = BAND_MAP.get(row['risk_band'], row['risk_band'])
        st.markdown(
            f"**{row['trust_code']}** &nbsp;·&nbsp; {badge} &nbsp;·&nbsp; "
            f"£{row['backlog_cost_per_bed']:,.0f}/bed",
            unsafe_allow_html=True
        )
    st.markdown("---")
    st.caption("High ≥ £5,000/bed · Significant ≥ £2,500 · Moderate ≥ £1,000 · Low < £1,000")

# ── Row 2: Trend chart + Energy cost chart ─────────────────────────────────────
st.markdown('<p class="section-header">Trends Over Time</p>', unsafe_allow_html=True)

col_trend, col_energy = st.columns(2)

with col_trend:
    fig_trend = px.line(
        trend, x='year', y='current_backlog_gbp', color='trust_code',
        markers=True,
        labels={'current_backlog_gbp': 'Backlog (£)', 'year': 'Year', 'trust_code': 'Trust'},
        title='Maintenance Backlog Trend (£)',
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        title_font=dict(size=14, color='#94a3b8'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', color='#64748b'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', color='#64748b', tickprefix='£'),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8')),
        margin=dict(l=20, r=20, t=40, b=20),
        height=340,
    )
    fig_trend.update_traces(line=dict(width=2.5), marker=dict(size=8))
    st.plotly_chart(fig_trend, use_container_width=True)

with col_energy:
    fig_energy = px.line(
        energy, x='year', y='energy_cost_per_bed', color='trust_code',
        markers=True,
        labels={'energy_cost_per_bed': 'Energy Cost / Bed (£)', 'year': 'Year', 'trust_code': 'Trust'},
        title='Energy Cost per Bed (£)',
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig_energy.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        title_font=dict(size=14, color='#94a3b8'),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', color='#64748b'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', color='#64748b', tickprefix='£'),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8')),
        margin=dict(l=20, r=20, t=40, b=20),
        height=340,
    )
    fig_energy.update_traces(line=dict(width=2.5), marker=dict(size=8))
    st.plotly_chart(fig_energy, use_container_width=True)

# ── Row 3: Backlog % share stacked bar + YoY growth ────────────────────────────
st.markdown('<p class="section-header">Backlog Share & Growth</p>', unsafe_allow_html=True)

col_share, col_growth = st.columns(2)

with col_share:
    fig_share = px.bar(
        backlog_pt, x='year', y='backlog_percent', color='trust_code',
        barmode='stack',
        labels={'backlog_percent': 'Backlog Share (%)', 'year': 'Year', 'trust_code': 'Trust'},
        title='Backlog % Share by Trust per Year',
        color_discrete_sequence=px.colors.qualitative.Bold,
        text_auto='.1f',
    )
    fig_share.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        title_font=dict(size=14, color='#94a3b8'),
        xaxis=dict(showgrid=False, color='#64748b'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', color='#64748b', ticksuffix='%'),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8')),
        margin=dict(l=20, r=20, t=40, b=20),
        height=340,
    )
    st.plotly_chart(fig_share, use_container_width=True)

with col_growth:
    trend_filtered = trend[trend['backlog_growth_pct'].notna()].copy()
    fig_growth = px.bar(
        trend_filtered, x='year', y='backlog_growth_pct', color='trust_code',
        barmode='group',
        labels={'backlog_growth_pct': 'YoY Growth (%)', 'year': 'Year', 'trust_code': 'Trust'},
        title='Backlog YoY Growth (%) by Trust',
        color_discrete_sequence=px.colors.qualitative.Bold,
        text_auto='.1f',
    )
    fig_growth.add_hline(y=0, line_dash='dot', line_color='rgba(255,255,255,0.3)')
    fig_growth.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', family='Inter'),
        title_font=dict(size=14, color='#94a3b8'),
        xaxis=dict(showgrid=False, color='#64748b'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.06)', color='#64748b', ticksuffix='%'),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8')),
        margin=dict(l=20, r=20, t=40, b=20),
        height=340,
    )
    st.plotly_chart(fig_growth, use_container_width=True)

# ── Row 4: Raw data tables ─────────────────────────────────────────────────────
st.markdown('<p class="section-header">Data Explorer</p>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Trust Summary", "📈 Backlog Trend", "⚡ Energy"])

with tab1:
    display_summary = summary.copy()
    display_summary['backlog_gbp']       = display_summary['backlog_gbp'].apply(lambda x: f"£{x:,.0f}")
    display_summary['energy_cost_gbp']   = display_summary['energy_cost_gbp'].apply(lambda x: f"£{x:,.0f}")
    display_summary['energy_cost_per_bed'] = display_summary['energy_cost_per_bed'].apply(lambda x: f"£{x:,.0f}")
    display_summary['backlog_cost_per_bed'] = display_summary['backlog_cost_per_bed'].apply(lambda x: f"£{x:,.0f}")
    display_summary['backlog_change_pct'] = display_summary['backlog_change_pct'].apply(
        lambda x: f"{'▲' if x > 0 else '▼'} {abs(x):.1f}%" if pd.notna(x) else "—"
    )
    st.dataframe(display_summary, use_container_width=True, hide_index=True)

with tab2:
    display_trend = trend.copy()
    for col in ['current_backlog_gbp', 'prev_year_backlog_gbp', 'backlog_growth_gbp']:
        display_trend[col] = display_trend[col].apply(
            lambda x: f"£{x:,.0f}" if pd.notna(x) else "—"
        )
    display_trend['backlog_growth_pct'] = display_trend['backlog_growth_pct'].apply(
        lambda x: f"{'▲' if x > 0 else '▼'} {abs(x):.1f}%" if pd.notna(x) else "—"
    )
    st.dataframe(display_trend, use_container_width=True, hide_index=True)

with tab3:
    display_energy = energy.copy()
    display_energy['total_energy_cost']  = display_energy['total_energy_cost'].apply(lambda x: f"£{x:,.0f}")
    display_energy['energy_cost_per_bed'] = display_energy['energy_cost_per_bed'].apply(lambda x: f"£{x:,.0f}")
    st.dataframe(display_energy, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("🏥 Hospital FM Intelligence Hub · NHS ERIC Data · Built with Bruin + DuckDB + Streamlit")
