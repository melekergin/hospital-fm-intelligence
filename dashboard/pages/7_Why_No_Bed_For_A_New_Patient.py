import pandas as pd
import plotly.express as px
import streamlit as st

from lib import (
    apply_base_styles,
    ordered_years,
    pipeline_ready,
    query,
    render_glossary,
    render_how_to_read,
    render_setup_message,
)


st.set_page_config(
    page_title="Why Is There No Bed?",
    page_icon="🛏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

cockpit = query(
    """
    SELECT *
    FROM kpi_trust_operational_cockpit
    ORDER BY year_sort DESC, total_backlog_gbp DESC
    """
)

years = ordered_years(cockpit, descending=True)
selected_year = st.sidebar.selectbox("Year", years, index=0)
year_view = cockpit[cockpit["year"] == selected_year].copy()
trust_options = year_view.sort_values("total_backlog_gbp", ascending=False)["trust_code"].tolist()
selected_trust = st.sidebar.selectbox("Trust", trust_options, index=0)

trust_row = year_view[year_view["trust_code"] == selected_trust].iloc[0]
peer_view = year_view.copy()

st.title("Why is there no bed for a new patient?")
st.write(
    "Often the answer is not simply 'the hospital is full'. A bed can exist physically but still not be ready for "
    "use because the room is not turned around, equipment is unavailable, building issues are unresolved, or the "
    "patient pathway around procedures and discharge is slowing down."
)

render_glossary(
    ["Backlog", "Estate", "Work Order", "Compliance", "AEMP / ZSVA"],
    title="Words You May Need On This Page",
)
render_how_to_read(
    "How to use this page",
    "Read the four blockers first. Then look at how the selected trust compares with peers. The aim is not to prove "
    "one single cause, but to show the hidden FM conditions that can make patient flow harder.",
)

blocker_cols = st.columns(4)
blockers = [
    (
        "Room turnaround",
        "Beds do not become usable again until spaces are cleaned and made ready.",
        f"Cleaning spend: GBP {trust_row['cleaning_cost_per_m2']:,.2f} per m2",
    ),
    (
        "Building pressure",
        "Old unresolved repairs can quietly reduce flexibility in rooms, wards, or support areas.",
        f"Backlog: GBP {trust_row['backlog_cost_per_m2']:,.2f} per m2",
    ),
    (
        "Equipment readiness",
        "A bed space may still be blocked if pumps, monitors, ventilation, or nearby support systems are not ready.",
        f"Overdue assets: {int(trust_row['overdue_assets'])}",
    ),
    (
        "Procedure flow",
        "Delays in sterile processing or downstream procedures can slow the movement of patients through the hospital.",
        f"AEMP dispatch delay: {trust_row['avg_dispatch_delay_minutes']:.1f} minutes",
    ),
]
for col, (title, body, metric) in zip(blocker_cols, blockers):
    col.markdown(
        f"""
        <div class="story-card">
            <h3>{title}</h3>
            <p>{body}</p>
            <p><strong>{metric}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

peer_comparison = pd.DataFrame(
    [
        {
            "signal": "Cleaning pressure",
            "selected_trust": trust_row["cleaning_cost_per_m2"],
            "peer_median": peer_view["cleaning_cost_per_m2"].median(),
            "unit": "GBP per m2",
        },
        {
            "signal": "Repair backlog",
            "selected_trust": trust_row["backlog_cost_per_m2"],
            "peer_median": peer_view["backlog_cost_per_m2"].median(),
            "unit": "GBP per m2",
        },
        {
            "signal": "Overdue inspections",
            "selected_trust": trust_row["overdue_assets"],
            "peer_median": peer_view["overdue_assets"].median(),
            "unit": "assets",
        },
        {
            "signal": "Sterile dispatch delay",
            "selected_trust": trust_row["avg_dispatch_delay_minutes"],
            "peer_median": peer_view["avg_dispatch_delay_minutes"].median(),
            "unit": "minutes",
        },
    ]
)
comparison_long = peer_comparison.melt(
    id_vars=["signal", "unit"],
    value_vars=["selected_trust", "peer_median"],
    var_name="group",
    value_name="value",
)
comparison_long["group"] = comparison_long["group"].map(
    {"selected_trust": selected_trust, "peer_median": "Peer median"}
)

row1 = st.columns(2)

with row1[0]:
    st.subheader("Which hidden blockers look heavier than the peer median?")
    render_how_to_read(
        "What to notice",
        "If the selected trust is above the peer median, that does not automatically explain every bed delay. It does show where this trust is carrying more hidden operational pressure than its peers.",
    )
    fig = px.bar(
        comparison_long,
        x="signal",
        y="value",
        color="group",
        barmode="group",
        labels={"signal": "Hidden blocker", "value": "Value", "group": "Comparison"},
        color_discrete_map={selected_trust: "#b23a48", "Peer median": "#2c7da0"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig, use_container_width=True)

with row1[1]:
    st.subheader("How does this trust compare with peers overall?")
    render_how_to_read(
        "How to read this bubble chart",
        "Further right means higher cleaning pressure. Higher up means higher repair backlog. Bigger bubbles mean more overdue inspections. Darker colour means more sterile dispatch delay.",
    )
    fig = px.scatter(
        peer_view,
        x="cleaning_cost_per_m2",
        y="backlog_cost_per_m2",
        size="overdue_assets",
        color="avg_dispatch_delay_minutes",
        hover_name="trust_name",
        text="trust_code",
        color_continuous_scale=["#2c7da0", "#d17b0f", "#b23a48"],
        labels={
            "cleaning_cost_per_m2": "Cleaning pressure (GBP per m2)",
            "backlog_cost_per_m2": "Repair backlog (GBP per m2)",
            "avg_dispatch_delay_minutes": "Sterile dispatch delay (min)",
        },
    )
    fig.update_traces(
        textposition="top center",
        marker_line_width=[3 if code == selected_trust else 0 for code in peer_view["trust_code"]],
        marker_line_color="#13293d",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("A simple explanation path")
path_cols = st.columns(4)
steps = [
    (
        "1. A patient needs a bed",
        "The admission or transfer decision is ready, but the receiving space must also be ready.",
    ),
    (
        "2. The bed space is not yet usable",
        "Cleaning, equipment readiness, or a local estate issue can delay handover of the space.",
    ),
    (
        "3. Flow slows elsewhere too",
        "If procedures, sterile processing, or discharge flow slow down, beds upstream and downstream stay occupied longer.",
    ),
    (
        "4. The front door feels the pressure",
        "The visible problem becomes 'no bed available', even though several hidden operational issues may be sitting underneath it.",
    ),
]
for col, (title, body) in zip(path_cols, steps):
    col.markdown(
        f"""
        <div class="story-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Selected trust summary")
st.dataframe(
    pd.DataFrame(
        [
            {
                "trust_code": trust_row["trust_code"],
                "trust_name": trust_row["trust_name"],
                "region": trust_row["region"],
                "site_count": trust_row["site_count"],
                "backlog_cost_per_m2": trust_row["backlog_cost_per_m2"],
                "cleaning_cost_per_m2": trust_row["cleaning_cost_per_m2"],
                "energy_cost_per_m2": trust_row["energy_cost_per_m2"],
                "overdue_assets": trust_row["overdue_assets"],
                "action_required_assets": trust_row["action_required_assets"],
                "avg_dispatch_delay_minutes": trust_row["avg_dispatch_delay_minutes"],
                "aemp_cycle_count": trust_row["aemp_cycle_count"],
            }
        ]
    ),
    use_container_width=True,
    hide_index=True,
)

st.info(
    "The point of this page is not that FM alone explains bed shortages. It is that bed availability is shaped by many hidden readiness conditions, and FM is one of the most important of them."
)
