import plotly.express as px
import streamlit as st

from lib import (
    apply_base_styles,
    apply_filters,
    filter_sidebar,
    load_real_metrics,
    pipeline_ready,
    query,
    render_setup_message,
)


st.set_page_config(
    page_title="Hospital FM Intelligence Hub",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

summary = load_real_metrics()
selected_years, selected_regions, selected_trusts = filter_sidebar(summary)
filtered = apply_filters(summary, selected_years, selected_regions, selected_trusts)

if filtered.empty:
    st.warning("No trusts match the current filters.")
    st.stop()

latest_year = filtered["year_sort"].max()
latest = filtered[filtered["year_sort"] == latest_year].copy()
latest_year_label = latest["year"].iloc[0]
years = sorted(filtered["year"].unique().tolist(), reverse=True)
aemp = query(
    """
    SELECT *
    FROM kpi_aemp_process_summary
    ORDER BY cycle_count DESC
    """
)
aemp = aemp[
    aemp["year"].isin(selected_years)
    & aemp["region"].isin(selected_regions)
    & aemp["trust_code"].isin(selected_trusts)
].copy()
aemp_latest = aemp[aemp["year"] == latest_year_label].copy() if not aemp.empty else aemp

st.markdown(
    f"""
    <div class="hero">
        <div class="section-label">Story Entry</div>
        <h1>Hospital FM Intelligence Hub</h1>
        <p><strong>A Day in the Life of NHS Facility Management</strong></p>
        <p>
            This app combines official NHS ERIC estate data with synthetic hospital operations to explain how
            facility management supports clinical care. The current live view spans estate pressure, maintenance,
            compliance, and AEMP across {len(latest)} trusts in {latest_year_label}.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

overview_cols = st.columns(4)
overview_cols[0].metric("Years in view", f"{len(years)}")
overview_cols[1].metric("Trusts in view", f"{len(latest)}")
overview_cols[2].metric("Backlog total", f"GBP {latest['total_backlog_gbp'].sum()/1e9:.1f}B")
overview_cols[3].metric(
    "AEMP conformity",
    f"{aemp_latest['conformity_rate_pct'].mean():.2f}%" if not aemp_latest.empty else "n/a",
)

st.write("")
st.markdown("### Start Here")

nav_cols = st.columns(3)
nav_cols[0].markdown(
    """
    <div class="nav-card">
        <h3>Story Path</h3>
        <p><strong>Go to:</strong> <code>1_A_Day_in_FM</code></p>
        <p>Best first stop for understanding the hospital day from cleaning through AEMP and backlog review.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
nav_cols[1].markdown(
    """
    <div class="nav-card">
        <h3>Operational Modules</h3>
        <p><strong>Go to:</strong> <code>3_Equipment_Journey</code>, <code>4_Compliance_Control</code>, <code>6_AEMP_Process</code></p>
        <p>Use these pages when you want process depth in maintenance, compliance, or sterile processing.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
nav_cols[2].markdown(
    """
    <div class="nav-card">
        <h3>Trust Cockpit</h3>
        <p><strong>Go to:</strong> <code>5_Trust_Drilldown</code></p>
        <p>Best page for a single-trust operational view that combines estate pressure, work orders, compliance, and AEMP.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
story_cols = st.columns(4)
story_cols[0].markdown(
    """
    <div class="story-card">
        <h3>6:30 AM</h3>
        <p>Cleaning teams prepare the estate so clinical activity can start safely.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
story_cols[1].markdown(
    """
    <div class="story-card">
        <h3>8:00 AM</h3>
        <p>Engineering teams keep equipment and infrastructure available under real estate pressure.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
story_cols[2].markdown(
    """
    <div class="story-card">
        <h3>11:00 AM</h3>
        <p>AEMP releases sterile sets back to theatres and clinical areas with traceability.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
story_cols[3].markdown(
    """
    <div class="story-card">
        <h3>2:00 PM</h3>
        <p>Leaders review backlog, compliance, and operational risk before those issues affect care.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

chart_cols = st.columns(2)
with chart_cols[0]:
    st.subheader("Latest Trust Snapshot")
    snapshot_fig = px.scatter(
        latest,
        x="energy_cost_per_m2",
        y="cleaning_cost_per_m2",
        size="total_backlog_gbp",
        color="backlog_risk_band_by_m2",
        hover_name="trust_name",
        text="trust_code",
        color_discrete_map={
            "High": "#b23a48",
            "Significant": "#d17b0f",
            "Moderate": "#2c7da0",
            "Low": "#4b8f29",
        },
        labels={
            "energy_cost_per_m2": "Energy cost per m2 (GBP)",
            "cleaning_cost_per_m2": "Cleaning cost per m2 (GBP)",
            "backlog_risk_band_by_m2": "Backlog risk",
        },
    )
    snapshot_fig.update_traces(textposition="top center")
    snapshot_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(snapshot_fig, use_container_width=True)

with chart_cols[1]:
    st.subheader("Backlog Pressure Trend")
    backlog_fig = px.line(
        filtered,
        x="year",
        y="backlog_cost_per_m2",
        color="trust_code",
        markers=True,
        labels={"backlog_cost_per_m2": "Backlog per m2 (GBP)", "year": "Year", "trust_code": "Trust"},
    )
    backlog_fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(backlog_fig, use_container_width=True)

st.subheader("Current Live Domain Signals")
signal_cols = st.columns(3)
signal_cols[0].markdown(
    f"<div class='kpi-note'><strong>Estate</strong><br>Average backlog {latest['backlog_cost_per_m2'].mean():,.2f} GBP per m2</div>",
    unsafe_allow_html=True,
)
signal_cols[1].markdown(
    f"<div class='kpi-note'><strong>Maintenance</strong><br>Average energy {latest['energy_cost_per_m2'].mean():,.2f} GBP per m2</div>",
    unsafe_allow_html=True,
)
signal_cols[2].markdown(
    (
        f"<div class='kpi-note'><strong>AEMP</strong><br>Average traceability {aemp_latest['traceability_rate_pct'].mean():,.2f}%</div>"
        if not aemp_latest.empty
        else "<div class='kpi-note'><strong>AEMP</strong><br>No data in current filter</div>"
    ),
    unsafe_allow_html=True,
)

st.info(
    "Use this page as the front door. The narrative starts in `1_A_Day_in_FM`, the trust cockpit lives in `5_Trust_Drilldown`, and the process-specific pages deepen the story."
)
