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
    page_title="One Hospital, Behind The Scenes",
    page_icon="🏢",
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
orders = query(
    """
    SELECT *
    FROM fact_equipment_work_orders
    ORDER BY event_start_ts DESC
    """
)
assets = query(
    """
    SELECT *
    FROM fact_equipment_compliance_assets
    ORDER BY compliance_risk_rank, days_from_due_date DESC
    """
)
aemp_shift = query(
    """
    SELECT *
    FROM kpi_aemp_shift_load
    ORDER BY cycle_count DESC
    """
)

years = ordered_years(cockpit, descending=True)
selected_year = st.sidebar.selectbox("Year", years, index=0)
year_view = cockpit[cockpit["year"] == selected_year].copy()
trust_options = year_view.sort_values("total_backlog_gbp", ascending=False)["trust_code"].tolist()
selected_trust = st.sidebar.selectbox("Trust", trust_options, index=0)

trust_row = year_view[year_view["trust_code"] == selected_trust].iloc[0]
trust_orders = orders[(orders["year"] == selected_year) & (orders["trust_code"] == selected_trust)].copy()
trust_assets = assets[(assets["year"] == selected_year) & (assets["trust_code"] == selected_trust)].copy()
trust_aemp_shift = aemp_shift[(aemp_shift["year"] == selected_year) & (aemp_shift["trust_code"] == selected_trust)].copy()

st.title(f"One hospital, behind the scenes: {trust_row['trust_name']}")
st.write(
    "This page brings the main hospital FM stories together for one trust. It shows building pressure, equipment "
    "reliability, inspection risk, work-order flow, and sterile services in one place so you can see how these "
    "operational problems connect."
)

render_glossary(
    ["Trust", "Backlog", "Work Order", "Compliance", "AEMP / ZSVA"],
    title="Key Terms On This Page",
)
render_how_to_read(
    "How to use this page",
    "Start with the headline signals to understand the overall condition of the trust. Then look at the story cards "
    "and charts below to see where pressure is building: buildings, equipment, inspections, workflow, or sterile services.",
)

metric_cols = st.columns(8)
metric_cols[0].metric("Repair backlog", f"GBP {trust_row['total_backlog_gbp']/1e6:,.1f}M")
metric_cols[1].metric("Energy spend", f"GBP {trust_row['total_energy_cost_gbp']/1e6:,.1f}M")
metric_cols[2].metric("Cleaning spend", f"GBP {trust_row['total_cleaning_cost_gbp']/1e6:,.1f}M")
metric_cols[3].metric("Tracked assets", f"{int(trust_row['asset_count'])}")
metric_cols[4].metric("Overdue inspections", f"{int(trust_row['overdue_assets'])}")
metric_cols[5].metric("Maintenance jobs", f"{int(trust_row['total_work_orders'])}")
metric_cols[6].metric("Sterile cycles", f"{int(trust_row['aemp_cycle_count'])}")
metric_cols[7].metric("Sterile quality", f"{trust_row['conformity_rate_pct']:.2f}%")

note_cols = st.columns(6)
note_cols[0].markdown(
    f"<div class='kpi-note'><strong>Estate pressure</strong><br>{trust_row['backlog_risk_band_by_m2']}</div>",
    unsafe_allow_html=True,
)
note_cols[1].markdown(
    f"<div class='kpi-note'><strong>Equipment availability</strong><br>{trust_row['avg_availability_pct']:.2f}%</div>",
    unsafe_allow_html=True,
)
note_cols[2].markdown(
    f"<div class='kpi-note'><strong>Inspection compliance</strong><br>{trust_row['compliance_rate_pct']:.2f}%</div>",
    unsafe_allow_html=True,
)
note_cols[3].markdown(
    f"<div class='kpi-note'><strong>Average job cost</strong><br>GBP {trust_row['avg_work_order_cost_gbp']:,.0f}</div>",
    unsafe_allow_html=True,
)
note_cols[4].markdown(
    f"<div class='kpi-note'><strong>Instrument traceability</strong><br>{trust_row['traceability_rate_pct']:.2f}%</div>",
    unsafe_allow_html=True,
)
note_cols[5].markdown(
    f"<div class='kpi-note'><strong>Reprocess rate</strong><br>{trust_row['reprocess_rate_pct']:.2f}%</div>",
    unsafe_allow_html=True,
)

st.subheader("What is happening in this trust right now?")
story_cols = st.columns(5)
cards = [
    (
        "Buildings",
        f"{trust_row['site_count']} sites and {trust_row['gross_internal_floor_area_m2']:,.0f} m2 must be kept safe and usable. "
        f"Backlog pressure is {trust_row['backlog_cost_per_m2']:,.2f} GBP per m2.",
    ),
    (
        "Equipment",
        f"{int(trust_row['planned_events'])} planned maintenance events and {int(trust_row['corrective_events'])} breakdown-related events "
        f"led to {trust_row['downtime_hours']:,.0f} downtime hours.",
    ),
    (
        "Inspections",
        f"{int(trust_row['overdue_assets'])} assets are overdue and {int(trust_row['action_required_assets'])} need action now.",
    ),
    (
        "Workflow",
        f"{int(trust_row['status_in_progress'])} jobs are in progress, {int(trust_row['status_technically_complete'])} are technically complete, "
        f"and {int(trust_row['status_closed'])} are fully closed.",
    ),
    (
        "Sterile services",
        f"{int(trust_row['aemp_cycle_count'])} cycles were processed with {trust_row['avg_dispatch_delay_minutes']:.1f} minutes average dispatch delay.",
    ),
]
for col, (title, body) in zip(story_cols, cards):
    col.markdown(
        f"""
        <div class="story-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

row1 = st.columns(2)

with row1[0]:
    st.subheader("How expensive is it to carry the estate?")
    render_how_to_read(
        "What to notice",
        "Backlog shows unresolved repair burden. Energy and cleaning show the day-to-day cost of keeping the hospital usable. "
        "A trust with high values across all three is under both long-term and daily estate pressure.",
    )
    estate_chart_df = [
        ("Backlog per m2", trust_row["backlog_cost_per_m2"]),
        ("Energy per m2", trust_row["energy_cost_per_m2"]),
        ("Cleaning per m2", trust_row["cleaning_cost_per_m2"]),
    ]
    fig = px.bar(
        x=[x[0] for x in estate_chart_df],
        y=[x[1] for x in estate_chart_df],
        labels={"x": "Estate signal", "y": "GBP per m2"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with row1[1]:
    st.subheader("Where are maintenance jobs getting stuck?")
    render_how_to_read(
        "Why this matters",
        "A healthy flow moves jobs from notification to closure. If many orders sit in the middle states, the trust may be struggling to turn maintenance requests into completed work.",
    )
    workflow_chart_df = [
        ("Notification", trust_row["status_notification"]),
        ("Planning", trust_row["status_planning"]),
        ("Approved", trust_row["status_approved"]),
        ("In Progress", trust_row["status_in_progress"]),
        ("Technically Complete", trust_row["status_technically_complete"]),
        ("Closed", trust_row["status_closed"]),
    ]
    fig = px.bar(
        x=[x[0] for x in workflow_chart_df],
        y=[x[1] for x in workflow_chart_df],
        labels={"x": "Work-order stage", "y": "Jobs"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

row2 = st.columns(2)

with row2[0]:
    st.subheader("Which equipment groups create the biggest maintenance burden?")
    render_how_to_read(
        "How to read this bubble chart",
        "Farther right means more downtime. Higher up means more maintenance cost. Bigger bubbles mean more work orders. "
        "Categories in the upper-right deserve attention because they combine disruption and cost.",
    )
    if not trust_orders.empty:
        category_rollup = (
            trust_orders.groupby("equipment_category", as_index=False)
            .agg(
                work_orders=("event_id", "count"),
                downtime_hours=("downtime_hours", "sum"),
                maintenance_cost_gbp=("maintenance_cost_gbp", "sum"),
            )
            .sort_values("maintenance_cost_gbp", ascending=False)
        )
        fig = px.scatter(
            category_rollup,
            x="downtime_hours",
            y="maintenance_cost_gbp",
            size="work_orders",
            color="equipment_category",
            text="equipment_category",
            labels={
                "downtime_hours": "Downtime hours",
                "maintenance_cost_gbp": "Maintenance cost (GBP)",
                "work_orders": "Work orders",
            },
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.55)",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No equipment work-order data is available for the current selection.")

with row2[1]:
    st.subheader("How risky is the inspection picture?")
    render_how_to_read(
        "What to notice",
        "More assets in the red and orange categories means more safety and compliance pressure. Assets that are overdue or action-required deserve the fastest attention.",
    )
    if not trust_assets.empty:
        bucket_rollup = (
            trust_assets.groupby("compliance_risk_bucket", as_index=False)
            .size()
            .rename(columns={"size": "asset_count"})
        )
        fig = px.bar(
            bucket_rollup,
            x="compliance_risk_bucket",
            y="asset_count",
            color="compliance_risk_bucket",
            labels={"compliance_risk_bucket": "Inspection risk bucket", "asset_count": "Assets"},
            color_discrete_map={
                "Action Required": "#8c1c13",
                "Critical Overdue": "#b23a48",
                "Overdue": "#d17b0f",
                "Due Soon": "#2c7da0",
                "In Date": "#4b8f29",
            },
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.55)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No inspection-risk data is available for the current selection.")

row3 = st.columns(2)

with row3[0]:
    st.subheader("When is sterile processing busiest?")
    render_how_to_read(
        "Why this matters",
        "Cycle volume by shift shows when sterile services are under the most load. If one shift carries much more volume, delays there can affect theatres and procedures later.",
    )
    if not trust_aemp_shift.empty:
        fig = px.bar(
            trust_aemp_shift.groupby("shift_name", as_index=False)["cycle_count"].sum(),
            x="shift_name",
            y="cycle_count",
            labels={"shift_name": "AEMP shift", "cycle_count": "Cycles"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.55)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sterile-services shift data is available for the current selection.")

with row3[1]:
    st.subheader("Where does sterile processing slow down?")
    render_how_to_read(
        "How to read this",
        "The tallest bar marks the step where the most cycles experienced a bottleneck. That gives a quick hint about where sterile services may need closer operational attention.",
    )
    if not trust_aemp_shift.empty:
        fig = px.bar(
            trust_aemp_shift.groupby("bottleneck_stage", as_index=False)["cycle_count"]
            .sum()
            .sort_values("cycle_count", ascending=False),
            x="bottleneck_stage",
            y="cycle_count",
            labels={"bottleneck_stage": "Bottleneck stage", "cycle_count": "Cycles"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.55)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sterile-services bottleneck data is available for the current selection.")

st.subheader("Recent maintenance jobs")
render_how_to_read(
    "Why include the table",
    "This is the detailed view behind the summary numbers. It helps show what kinds of jobs are being raised, what status they are in, and what equipment is involved.",
)
st.dataframe(
    trust_orders[
        [
            "event_id",
            "asset_id",
            "equipment_category",
            "event_type",
            "priority",
            "work_order_status",
            "work_center",
            "planner_group",
            "event_start_ts",
            "downtime_hours",
            "maintenance_cost_gbp",
            "failure_mode",
            "compliance_status",
        ]
    ].head(30),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Assets needing the closest inspection attention")
render_how_to_read(
    "What this table helps answer",
    "If someone asked which devices should be checked first, this is the starting point. The table puts the highest inspection risk at the top.",
)
trust_asset_risk_view = trust_assets.sort_values(
    ["compliance_risk_rank", "days_from_due_date"],
    ascending=[True, False],
)
st.dataframe(
    trust_asset_risk_view[
        [
            "asset_id",
            "site_code",
            "equipment_category",
            "criticality",
            "inspection_outcome",
            "compliance_status",
            "compliance_risk_bucket",
            "days_from_due_date",
            "next_inspection_due_date",
            "acquisition_value_gbp",
        ]
    ].head(30),
    use_container_width=True,
    hide_index=True,
)

if not trust_aemp_shift.empty:
    st.subheader("Sterile-services shift detail")
    st.dataframe(
        trust_aemp_shift[
            [
                "shift_name",
                "bottleneck_stage",
                "cycle_count",
                "avg_cycle_duration_minutes",
                "reprocess_rate_pct",
            ]
        ].sort_values("cycle_count", ascending=False),
        use_container_width=True,
        hide_index=True,
    )
