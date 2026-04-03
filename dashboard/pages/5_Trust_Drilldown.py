import plotly.express as px
import streamlit as st

from lib import apply_base_styles, pipeline_ready, query, render_setup_message


st.set_page_config(
    page_title="Trust Drilldown",
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

years = sorted(cockpit["year"].unique().tolist(), reverse=True)
selected_year = st.sidebar.selectbox("Year", years, index=0)
year_view = cockpit[cockpit["year"] == selected_year].copy()
trust_options = year_view.sort_values("total_backlog_gbp", ascending=False)["trust_code"].tolist()
selected_trust = st.sidebar.selectbox("Trust", trust_options, index=0)

trust_row = year_view[year_view["trust_code"] == selected_trust].iloc[0]
trust_orders = orders[(orders["year"] == selected_year) & (orders["trust_code"] == selected_trust)].copy()
trust_assets = assets[(assets["year"] == selected_year) & (assets["trust_code"] == selected_trust)].copy()
trust_aemp_shift = aemp_shift[(aemp_shift["year"] == selected_year) & (aemp_shift["trust_code"] == selected_trust)].copy()

st.title(f"Trust Drilldown: {trust_row['trust_name']}")
st.write(
    "This page is the operational cockpit for a single trust. It combines estate pressure from official ERIC data with synthetic maintenance, compliance, and AEMP process exposure."
)

metric_cols = st.columns(8)
metric_cols[0].metric("Backlog", f"GBP {trust_row['total_backlog_gbp']/1e6:,.1f}M")
metric_cols[1].metric("Energy", f"GBP {trust_row['total_energy_cost_gbp']/1e6:,.1f}M")
metric_cols[2].metric("Cleaning", f"GBP {trust_row['total_cleaning_cost_gbp']/1e6:,.1f}M")
metric_cols[3].metric("Assets", f"{int(trust_row['asset_count'])}")
metric_cols[4].metric("Overdue assets", f"{int(trust_row['overdue_assets'])}")
metric_cols[5].metric("Work orders", f"{int(trust_row['total_work_orders'])}")
metric_cols[6].metric("AEMP cycles", f"{int(trust_row['aemp_cycle_count'])}")
metric_cols[7].metric("AEMP conformity", f"{trust_row['conformity_rate_pct']:.2f}%")

note_cols = st.columns(6)
note_cols[0].markdown(
    f"<div class='kpi-note'><strong>Backlog risk</strong><br>{trust_row['backlog_risk_band_by_m2']}</div>",
    unsafe_allow_html=True,
)
note_cols[1].markdown(
    f"<div class='kpi-note'><strong>Availability</strong><br>{trust_row['avg_availability_pct']:.2f}%</div>",
    unsafe_allow_html=True,
)
note_cols[2].markdown(
    f"<div class='kpi-note'><strong>Compliance rate</strong><br>{trust_row['compliance_rate_pct']:.2f}%</div>",
    unsafe_allow_html=True,
)
note_cols[3].markdown(
    f"<div class='kpi-note'><strong>Avg work-order cost</strong><br>GBP {trust_row['avg_work_order_cost_gbp']:,.0f}</div>",
    unsafe_allow_html=True,
)
note_cols[4].markdown(
    f"<div class='kpi-note'><strong>AEMP traceability</strong><br>{trust_row['traceability_rate_pct']:.2f}%</div>",
    unsafe_allow_html=True,
)
note_cols[5].markdown(
    f"<div class='kpi-note'><strong>AEMP reprocess</strong><br>{trust_row['reprocess_rate_pct']:.2f}%</div>",
    unsafe_allow_html=True,
)

st.subheader("Operational Story")
story_cols = st.columns(5)
cards = [
    ("Estate", f"{trust_row['site_count']} sites, {trust_row['gross_internal_floor_area_m2']:,.0f} m2, backlog pressure {trust_row['backlog_cost_per_m2']:,.2f} GBP per m2."),
    ("Maintenance", f"{int(trust_row['planned_events'])} planned and {int(trust_row['corrective_events'])} corrective events with {trust_row['downtime_hours']:,.0f} downtime hours."),
    ("Compliance", f"{int(trust_row['overdue_assets'])} overdue assets and {int(trust_row['action_required_assets'])} action-required assets."),
    ("Workflow", f"{int(trust_row['status_in_progress'])} in progress, {int(trust_row['status_technically_complete'])} technically complete, {int(trust_row['status_closed'])} closed."),
    ("AEMP", f"{int(trust_row['aemp_cycle_count'])} cycles, {trust_row['conformity_rate_pct']:.2f}% conformity, {trust_row['avg_dispatch_delay_minutes']:.1f} minute dispatch delay."),
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
    estate_chart_df = [
        ("Backlog per m2", trust_row["backlog_cost_per_m2"]),
        ("Energy per m2", trust_row["energy_cost_per_m2"]),
        ("Cleaning per m2", trust_row["cleaning_cost_per_m2"]),
    ]
    fig = px.bar(
        x=[x[0] for x in estate_chart_df],
        y=[x[1] for x in estate_chart_df],
        labels={"x": "Metric", "y": "GBP per m2"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with row1[1]:
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
        labels={"x": "Work-order status", "y": "Orders"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

row2 = st.columns(2)

with row2[0]:
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

with row2[1]:
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
            labels={"compliance_risk_bucket": "Risk bucket", "asset_count": "Assets"},
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

row3 = st.columns(2)

with row3[0]:
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

with row3[1]:
    if not trust_aemp_shift.empty:
        fig = px.bar(
            trust_aemp_shift.groupby("bottleneck_stage", as_index=False)["cycle_count"].sum().sort_values("cycle_count", ascending=False),
            x="bottleneck_stage",
            y="cycle_count",
            labels={"bottleneck_stage": "AEMP bottleneck stage", "cycle_count": "Cycles"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.55)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Recent Work Orders")
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

st.subheader("Highest-Risk Assets")
st.dataframe(
    trust_assets[
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
    ].sort_values(["compliance_risk_rank", "days_from_due_date"], ascending=[True, False]).head(30),
    use_container_width=True,
    hide_index=True,
)

if not trust_aemp_shift.empty:
    st.subheader("AEMP Shift Profile")
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

st.info(
    "This cockpit now combines estate, maintenance, compliance, and AEMP. The next strong move is to improve navigation and visual cohesion across pages so the app reads like one intentional product."
)
