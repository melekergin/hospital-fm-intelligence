import streamlit as st

from lib import (
    apply_base_styles,
    apply_filters,
    filter_sidebar,
    load_real_metrics,
    pipeline_ready,
    query,
    render_glossary,
    render_how_to_read,
    render_next_steps,
    render_setup_message,
)


st.set_page_config(
    page_title="A Day In Hospital FM",
    page_icon="🕒",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

df = load_real_metrics()
selected_years, selected_regions, selected_trusts = filter_sidebar(df, trust_limit=15)
filtered = apply_filters(df, selected_years, selected_regions, selected_trusts)

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

if filtered.empty:
    st.warning("No trusts match the current filters.")
    st.stop()

latest_year = filtered["year_sort"].max()
latest = filtered[filtered["year_sort"] == latest_year].copy()
latest_year_label = latest["year"].iloc[0]
aemp_latest = aemp[aemp["year"] == latest_year_label].copy() if not aemp.empty else aemp

st.title("A day in the life of hospital FM")
st.write(
    "This page is the guided story version of the app. It follows one hospital day from early morning to evening "
    "and shows the hidden work that keeps beds, rooms, equipment, sterile sets, and patient flow moving."
)

render_glossary(
    ["Backlog", "Estate", "Planned Maintenance", "Corrective Maintenance", "AEMP / ZSVA", "Traceability"],
    title="Words You May Need On This Page",
)
render_how_to_read(
    "How to use this page",
    "Read left to right like a hospital day. For each moment, ask three things: what do patients see, what is FM "
    "doing in the background, and what happens if that support breaks down?",
)

st.subheader("The story of one day")
events = [
    (
        "6:00 AM",
        "Rooms must become usable again",
        "Patients may still be asleep, but FM-related work is already shaping the day. Cleaning and room turnaround decide whether the next patient can move in smoothly.",
        f"Current cleaning pressure: GBP {latest['cleaning_cost_per_m2'].mean():,.2f} per m2",
    ),
    (
        "8:00 AM",
        "Buildings and equipment are now under load",
        "As wards, imaging, and departments fill up, the estate has to hold. If lifts, ventilation, utilities, or equipment fail, clinical flow starts to bend around those failures.",
        f"Current energy pressure: GBP {latest['energy_cost_per_m2'].mean():,.2f} per m2",
    ),
    (
        "11:00 AM",
        "Sterile sets have to return at the right moment",
        "A procedure can be delayed even when staff and the patient are ready, simply because the right instruments have not returned clean, released, and traceable.",
        (
            f"Current AEMP conformity: {aemp_latest['conformity_rate_pct'].mean():,.2f}%"
            if not aemp_latest.empty
            else "AEMP data not available in current filter"
        ),
    ),
    (
        "2:00 PM",
        "Hidden backlog becomes visible pressure",
        "Backlog is unfinished repair and upgrade work. It sits quietly in the background until it starts showing up as inflexibility, cost, breakdowns, or delayed readiness.",
        f"Current backlog pressure: GBP {latest['backlog_cost_per_m2'].mean():,.2f} per m2",
    ),
    (
        "6:00 PM",
        "The hospital has to reset for tomorrow",
        "FM work does not end when visiting hours end. Rooms, assets, sterile services, maintenance flow, and infrastructure all need to be ready to start again the next morning.",
        f"Trusts in current view: {len(latest)}",
    ),
]

cols = st.columns(5)
for col, (time_label, title, body, metric) in zip(cols, events):
    col.markdown(
        f"""
        <div class="story-card">
            <h3>{time_label}</h3>
            <p><strong>{title}</strong></p>
            <p>{body}</p>
            <p><strong>{metric}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("What patients feel vs. what FM is doing")
comparison_cols = st.columns(3)
comparison_points = [
    (
        "What patients feel",
        "The room is ready. The bed is available. The scan happens. The procedure starts. The hospital feels organized.",
    ),
    (
        "What FM is doing",
        "Cleaning, inspections, maintenance, asset response, utilities support, sterile-services flow, and readiness work across the estate.",
    ),
    (
        "What happens when support slips",
        "Delays start to appear as blocked beds, broken equipment, overdue inspections, missing sterile sets, and hidden backlog pressure.",
    ),
]
for col, (title, body) in zip(comparison_cols, comparison_points):
    col.markdown(
        f"""
        <div class="story-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("What this means at trust level")
render_how_to_read(
    "Why this section matters",
    "These trust summaries keep the story anchored in something measurable. They are not there to overwhelm you. They are there to show that the hidden pressures in the story differ across hospitals.",
)

key_takeaway_cols = st.columns(3)
key_takeaway_cols[0].markdown(
    f"<div class='kpi-note'><strong>Bed and room pressure</strong><br>Average cleaning pressure is GBP {latest['cleaning_cost_per_m2'].mean():,.2f} per m2 across the current view.</div>",
    unsafe_allow_html=True,
)
key_takeaway_cols[1].markdown(
    f"<div class='kpi-note'><strong>Building pressure</strong><br>Average backlog pressure is GBP {latest['backlog_cost_per_m2'].mean():,.2f} per m2, which shapes how resilient the estate feels.</div>",
    unsafe_allow_html=True,
)
key_takeaway_cols[2].markdown(
    (
        f"<div class='kpi-note'><strong>Sterile-services signal</strong><br>Average dispatch delay is {aemp_latest['avg_dispatch_delay_minutes'].mean():,.1f} minutes.</div>"
        if not aemp_latest.empty
        else "<div class='kpi-note'><strong>Sterile-services signal</strong><br>No AEMP data in the current filter.</div>"
    ),
    unsafe_allow_html=True,
)

if not aemp_latest.empty:
    st.subheader("The sterile-services part of the story")
    render_how_to_read(
        "What to notice",
        "High conformity and traceability support reliable clinical flow. Rising reprocessing or dispatch delay is the sign that something in the sterile-services chain is starting to slow down.",
    )
    st.dataframe(
        aemp_latest[
            [
                "trust_code",
                "trust_name",
                "cycle_count",
                "conformity_rate_pct",
                "traceability_rate_pct",
                "reprocess_rate_pct",
                "avg_dispatch_delay_minutes",
            ]
        ].sort_values("cycle_count", ascending=False).head(10),
        use_container_width=True,
        hide_index=True,
    )

render_next_steps(
    "Where next?",
    [
        ("Why is there no bed?", "dashboard/pages/7_Why_No_Bed_For_A_New_Patient.py", "Continue into the patient-flow scenario"),
        ("Why buildings matter", "dashboard/pages/2_Why_Buildings_Matter.py", "Go deeper into estate pressure"),
        ("One hospital behind the scenes", "dashboard/pages/5_One_Hospital_Behind_The_Scenes.py", "See the full trust view"),
    ],
)

st.info(
    "The key idea is simple: hospital FM is not one invisible support function. It is a chain of readiness work that keeps care moving from morning to night."
)
