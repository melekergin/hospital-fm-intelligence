import streamlit as st

from lib import (
    apply_base_styles,
    apply_filters,
    filter_sidebar,
    load_real_metrics,
    ordered_years,
    pipeline_ready,
    query,
    render_glossary,
    render_setup_message,
)


st.set_page_config(
    page_title="Start Here",
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
years = ordered_years(filtered, descending=True)
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

st.title("Start here")
st.write(
    "This page is only the front door. Use it to choose a learning path. The actual storytelling happens inside the pages on the left."
)

render_glossary(
    ["Trust", "Estate", "Backlog", "Compliance", "AEMP / ZSVA"],
    title="FM Words Explained Simply",
)

overview_cols = st.columns(3)
overview_cols[0].markdown(
    f"<div class='kpi-note'><strong>Live scope</strong><br>{len(latest)} trusts across {len(years)} years</div>",
    unsafe_allow_html=True,
)
overview_cols[1].markdown(
    f"<div class='kpi-note'><strong>Current estate picture</strong><br>Backlog total GBP {latest['total_backlog_gbp'].sum()/1e9:.1f}B in {latest_year_label}</div>",
    unsafe_allow_html=True,
)
overview_cols[2].markdown(
    (
        f"<div class='kpi-note'><strong>Sterile services signal</strong><br>Average conformity {aemp_latest['conformity_rate_pct'].mean():.2f}%</div>"
        if not aemp_latest.empty
        else "<div class='kpi-note'><strong>Sterile services signal</strong><br>No data in current filter</div>"
    ),
    unsafe_allow_html=True,
)

st.markdown("### Choose a learning path")
st.caption("Simple navigation only. No detailed visuals on this page.")

nav_cols = st.columns(3)
nav_cols[0].markdown(
    """
    <div class="nav-card">
        <h3>Start with the big picture</h3>
        <p><strong>Pages:</strong> A Day In Hospital FM, Why Is There No Bed For A New Patient?</p>
        <p>Best for first-time users who want the simplest explanation of how hidden FM work affects patient flow.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
nav_cols[1].markdown(
    """
    <div class="nav-card">
        <h3>Follow equipment problems</h3>
        <p><strong>Pages:</strong> What Happens When Hospital Equipment Fails?, What Happens When A CT Scanner Fails?, What Happens When Inspections Are Overdue?</p>
        <p>Use this path to understand maintenance, breakdowns, inspections, work orders, and technician response.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
nav_cols[2].markdown(
    """
    <div class="nav-card">
        <h3>Follow theatre and hospital flow</h3>
        <p><strong>Pages:</strong> Why Surgery Can Be Delayed By Sterile Instruments, Why Buildings Matter, One Hospital Behind The Scenes</p>
        <p>Use this path to connect sterile services, estate pressure, and trust-level operational strain.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
finance_cols = st.columns(2)
finance_cols[0].markdown(
    """
    <div class="nav-card">
        <h3>Follow the money</h3>
        <p><strong>Page:</strong> Why Backlog Becomes A Money Problem</p>
        <p>Use this page to understand why deferred repairs are not only a technical risk but also a financial one.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
finance_cols[1].markdown(
    """
    <div class="nav-card">
        <h3>Then return to the operations pages</h3>
        <p><strong>Best follow-up:</strong> Why Buildings Matter or One Hospital Behind The Scenes</p>
        <p>That helps connect the financial story back to everyday hospital pressure and patient-facing consequences.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Suggested order")
order_cols = st.columns(4)
steps = [
    ("1", "A Day In Hospital FM", "Start with the guided explanation."),
    ("2", "Why Is There No Bed?", "See how many hidden blockers shape patient flow."),
    ("3", "CT Scanner Failure", "Follow a concrete equipment breakdown scenario."),
    ("4", "One Hospital Behind The Scenes", "Bring the full operational picture together."),
]
for col, (step, title, body) in zip(order_cols, steps):
    col.markdown(
        f"""
        <div class="story-card">
            <h3>{step}</h3>
            <p><strong>{title}</strong></p>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.info(
    "If the main page still appears as 'app' in the sidebar, that is Streamlit using the launcher filename. The cleanest next step would be renaming the launcher itself once we finish the content structure."
)
