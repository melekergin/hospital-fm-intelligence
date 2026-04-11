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
    render_next_steps,
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
    "Choose the hospital question that feels most interesting to you. This page should help you enter the app quickly, not make you read another full explanation first."
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

st.markdown("### Choose a path")
st.caption("Click a route below. The goal is to get readers to the interesting pages immediately.")

route_cols = st.columns(4)
routes = [
    (
        "I know nothing yet",
        "pages/1_A_Day_In_Hospital_FM.py",
        "Best first page for a guided explanation.",
        "Start with the simplest guided story of one hospital day.",
    ),
    (
        "Why is there no bed?",
        "pages/7_Why_No_Bed_For_A_New_Patient.py",
        "Patient-flow scenario with bed readiness and hidden blockers.",
        "Go straight to the most intuitive patient-flow question.",
    ),
    (
        "What if equipment fails?",
        "pages/8_What_Happens_When_A_CT_Scanner_Fails.py",
        "Concrete device failure scenario.",
        "Follow a CT scanner problem from fault to operational impact.",
    ),
    (
        "Where does the money go?",
        "pages/9_Why_Backlog_Becomes_A_Money_Problem.py",
        "Finance view through backlog and estate cost.",
        "See why backlog is a money problem, not only a maintenance problem.",
    ),
]
for col, (title, page, help_text, body) in zip(route_cols, routes):
    with col:
        col.markdown(
            f"""
            <div class="nav-card">
                <h3>{title}</h3>
                <p>{body}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link(page, label="Open this path", help=help_text)

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

render_next_steps(
    "Or jump into a specialist view",
    [
        ("Buildings", "dashboard/pages/2_Why_Buildings_Matter.py", "Estate pressure and building burden"),
        ("Equipment", "dashboard/pages/3_What_Happens_When_Hospital_Equipment_Fails.py", "Maintenance and equipment overview"),
        ("Inspections", "dashboard/pages/4_What_Happens_When_Inspections_Are_Overdue.py", "Compliance and overdue inspections"),
        ("Whole Trust", "dashboard/pages/5_One_Hospital_Behind_The_Scenes.py", "Integrated trust view"),
    ],
)

st.info(
    "If the main page still appears as 'app' in the sidebar, that is Streamlit using the launcher filename. The cleanest next step would be renaming the launcher itself once we finish the content structure."
)
