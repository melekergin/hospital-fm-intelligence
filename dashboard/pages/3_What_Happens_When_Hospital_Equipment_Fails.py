import plotly.express as px
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
    render_setup_message,
)


st.set_page_config(
    page_title="What Happens When Hospital Equipment Fails?",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

estate = load_real_metrics()
selected_years, selected_regions, selected_trusts = filter_sidebar(estate, trust_limit=20)
estate_filtered = apply_filters(estate, selected_years, selected_regions, selected_trusts)

if estate_filtered.empty:
    st.warning("No trusts match the current filters.")
    st.stop()

reliability = query("SELECT * FROM kpi_equipment_reliability ORDER BY maintenance_cost_gbp DESC")
compliance = query("SELECT * FROM kpi_equipment_compliance ORDER BY overdue_assets DESC, action_required_assets DESC")
work_order_flow = query("SELECT * FROM kpi_work_order_flow ORDER BY total_order_cost_gbp DESC")
work_order_aging = query("SELECT * FROM kpi_work_order_aging ORDER BY order_count DESC")
work_orders = query("SELECT * FROM fact_equipment_work_orders ORDER BY event_start_ts DESC")

reliability = reliability[
    reliability["year"].isin(selected_years)
    & reliability["region"].isin(selected_regions)
    & reliability["trust_code"].isin(selected_trusts)
].copy()
compliance = compliance[
    compliance["year"].isin(selected_years)
    & compliance["region"].isin(selected_regions)
    & compliance["trust_code"].isin(selected_trusts)
].copy()
work_order_flow = work_order_flow[
    work_order_flow["year"].isin(selected_years)
    & work_order_flow["region"].isin(selected_regions)
    & work_order_flow["trust_code"].isin(selected_trusts)
].copy()
work_order_aging = work_order_aging[
    work_order_aging["year"].isin(selected_years)
    & work_order_aging["region"].isin(selected_regions)
    & work_order_aging["trust_code"].isin(selected_trusts)
].copy()
work_orders = work_orders[
    work_orders["year"].isin(selected_years)
    & work_orders["region"].isin(selected_regions)
    & work_orders["trust_code"].isin(selected_trusts)
].copy()

if reliability.empty or compliance.empty or work_order_flow.empty:
    st.warning("No equipment data matches the current filters.")
    st.stop()

latest_year_label = estate_filtered[estate_filtered["year_sort"] == estate_filtered["year_sort"].max()]["year"].iloc[0]
estate_latest = estate_filtered[estate_filtered["year_sort"] == estate_filtered["year_sort"].max()].copy()
reliability_latest = reliability[reliability["year"] == latest_year_label].copy()
compliance_latest = compliance[compliance["year"] == latest_year_label].copy()
flow_latest = work_order_flow[work_order_flow["year"] == latest_year_label].copy()
orders_latest = work_orders[work_orders["year"] == latest_year_label].copy()

st.title("What happens when hospital equipment fails?")
st.write(
    "This page follows a common hospital problem: a device is installed, used, inspected, then one day it needs service or suddenly fails. The point is not just the machine. The point is what happens next for patients, technicians, and hospital flow."
)

render_glossary(
    ["Work Order", "Planned Maintenance", "Corrective Maintenance", "Compliance", "Trust"],
    title="Words You May Need On This Page",
)

device = st.selectbox(
    "Choose equipment type",
    sorted(reliability_latest["equipment_category"].unique().tolist()),
)

device_reliability = reliability_latest[reliability_latest["equipment_category"] == device].copy()
device_compliance = compliance_latest[compliance_latest["equipment_category"] == device].copy()
device_flow = flow_latest[flow_latest["equipment_category"] == device].copy()
device_orders = orders_latest[orders_latest["equipment_category"] == device].copy()
device_aging = work_order_aging[
    (work_order_aging["year"] == latest_year_label)
    & (work_order_aging["equipment_category"] == device)
].copy()

merged = device_reliability.merge(
    device_compliance[
        [
            "trust_code",
            "equipment_category",
            "overdue_assets",
            "action_required_assets",
            "compliance_rate_pct",
        ]
    ],
    on=["trust_code", "equipment_category"],
    how="left",
).merge(
    device_flow.groupby("trust_code", as_index=False).agg(
        avg_response_minutes=("avg_response_minutes", "mean"),
        avg_work_order_age_days=("avg_work_order_age_days", "mean"),
        response_sla_met_pct=("response_sla_met_pct", "mean"),
    ),
    on="trust_code",
    how="left",
).merge(
    estate_latest[
        [
            "trust_code",
            "trust_name",
            "region",
            "total_backlog_gbp",
            "backlog_cost_per_m2",
            "energy_cost_per_m2",
            "cleaning_cost_per_m2",
        ]
    ],
    on=["trust_code", "trust_name", "region"],
    how="left",
)

metric_cols = st.columns(7)
metric_cols[0].metric("Assets in view", f"{int(device_reliability['asset_count'].sum())}")
metric_cols[1].metric("Breakdowns", f"{int(device_reliability['corrective_events'].sum())}")
metric_cols[2].metric("Overdue inspections", f"{int(device_compliance['overdue_assets'].sum())}")
metric_cols[3].metric("Action required", f"{int(device_compliance['action_required_assets'].sum())}")
metric_cols[4].metric("Average availability", f"{device_reliability['availability_pct'].mean():.2f}%")
metric_cols[5].metric("Avg response", f"{device_flow['avg_response_minutes'].mean():.0f} min")
metric_cols[6].metric("SLA met", f"{device_flow['response_sla_met_pct'].mean():.1f}%")

story_cols = st.columns(5)
steps = [
    ("1. Arrives", "The equipment enters the hospital and becomes part of the asset register."),
    ("2. Lives in service", "It is used day after day in clinical or support work."),
    ("3. Needs attention", "A service date arrives or something fails unexpectedly."),
    ("4. Technician is informed", "A work order is created so a team can inspect, repair, or escalate."),
    ("5. Repaired or delayed", "The machine returns to service, or downtime starts affecting care."),
]
for col, (title, body) in zip(story_cols, steps):
    col.markdown(
        f"""
        <div class="story-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

render_how_to_read(
    "What this page teaches",
    "A device problem is rarely just a technical problem. It can affect appointments, diagnostics, patient movement, and staff workload. The charts below help you see where that pressure starts to show up.",
)

row1 = st.columns(2)

with row1[0]:
    st.subheader("Which trusts look most exposed for this equipment type?")
    fig = px.scatter(
        merged,
        x="backlog_cost_per_m2",
        y="failure_rate_per_asset",
        size="asset_count",
        color="compliance_rate_pct",
        hover_name="trust_name",
        text="trust_code",
        labels={
            "backlog_cost_per_m2": "Hidden estate pressure (backlog per m2)",
            "failure_rate_per_asset": "How often this equipment type breaks per asset",
            "compliance_rate_pct": "Inspection compliance %",
        },
        color_continuous_scale=["#b23a48", "#d17b0f", "#2c7da0", "#4b8f29"],
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig, use_container_width=True)
    render_how_to_read(
        "What to notice",
        "Dots further right are trusts with more hidden estate pressure. Dots higher up are trusts where this equipment breaks more often. If a dot is both right and high, that trust may be carrying multiple kinds of FM risk at once.",
    )

with row1[1]:
    st.subheader("Where are the work orders getting stuck?")
    status_order = ["Notification", "Planning", "Approved", "In Progress", "Technically Complete", "Closed"]
    flow_chart = px.bar(
        device_flow,
        x="work_order_status",
        y="order_count",
        color="event_type",
        category_orders={"work_order_status": status_order},
        labels={
            "work_order_status": "Work-order stage",
            "order_count": "Number of maintenance jobs",
            "event_type": "Type of job",
        },
    )
    flow_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(flow_chart, use_container_width=True)
    render_how_to_read(
        "How to read this",
        "This shows the maintenance queue. If many orders sit in early stages like notification or planning, work may be waiting to start. If many reach closed, the process is moving through.",
    )

row2 = st.columns(2)

with row2[0]:
    st.subheader("Which trusts have the biggest inspection problem?")
    compliance_chart = px.bar(
        device_compliance.sort_values("overdue_assets", ascending=False).head(12),
        x="trust_code",
        y=["overdue_assets", "action_required_assets"],
        barmode="group",
        labels={
            "value": "Number of assets",
            "trust_code": "Trust",
            "variable": "Inspection issue",
        },
    )
    compliance_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(compliance_chart, use_container_width=True)
    render_how_to_read(
        "Why this matters",
        "An overdue inspection does not always mean the device has already failed. It means the hospital is carrying more uncertainty and risk than it should.",
    )

with row2[1]:
    st.subheader("Where is the money going?")
    cost_chart = px.bar(
        merged.sort_values("maintenance_cost_gbp", ascending=False).head(12),
        x="trust_code",
        y="maintenance_cost_gbp",
        hover_name="trust_name",
        labels={
            "trust_code": "Trust",
            "maintenance_cost_gbp": "Maintenance cost (GBP)",
        },
    )
    cost_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(cost_chart, use_container_width=True)
    render_how_to_read(
        "What to notice",
        "High cost can mean a large asset base, many planned services, or expensive repairs. It is a clue, not a verdict. You need to look at downtime and inspection status too.",
    )

row3 = st.columns(2)

with row3[0]:
    st.subheader("How fast do technicians respond?")
    render_how_to_read(
        "Why this matters",
        "Status alone does not show delay. Response time shows how long it takes for someone to react after the issue is reported. Higher bars mean slower reaction.",
    )
    response_view = merged.sort_values("avg_response_minutes", ascending=False).head(12)
    fig = px.bar(
        response_view,
        x="trust_code",
        y="avg_response_minutes",
        color="response_sla_met_pct",
        hover_name="trust_name",
        labels={
            "trust_code": "Trust",
            "avg_response_minutes": "Average response time (minutes)",
            "response_sla_met_pct": "SLA met %",
        },
        color_continuous_scale=["#b23a48", "#d17b0f", "#4b8f29"],
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig, use_container_width=True)

with row3[1]:
    st.subheader("How old is the maintenance queue?")
    render_how_to_read(
        "How to read this",
        "This shows how long orders have been open or took to resolve. More volume in older buckets means work is aging in the queue instead of being turned around quickly.",
    )
    if not device_aging.empty:
        aging_rollup = (
            device_aging.groupby("work_order_age_bucket", as_index=False)["order_count"]
            .sum()
        )
        bucket_order = ["Under 1 day", "1-3 days", "3-7 days", "1-2 weeks", "Over 2 weeks"]
        fig = px.bar(
            aging_rollup,
            x="work_order_age_bucket",
            y="order_count",
            category_orders={"work_order_age_bucket": bucket_order},
            labels={"work_order_age_bucket": "Queue age", "order_count": "Orders"},
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.55)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No work-order aging data is available for this selection.")

st.subheader(f"{device}: trust-level view")
st.dataframe(
    merged[
        [
            "trust_code",
            "trust_name",
            "region",
            "asset_count",
            "planned_events",
            "corrective_events",
            "downtime_hours",
            "maintenance_cost_gbp",
            "failure_rate_per_asset",
            "mttr_hours",
            "availability_pct",
            "overdue_assets",
            "action_required_assets",
            "compliance_rate_pct",
            "avg_response_minutes",
            "avg_work_order_age_days",
            "response_sla_met_pct",
            "backlog_cost_per_m2",
            "energy_cost_per_m2",
            "cleaning_cost_per_m2",
        ]
    ].sort_values("maintenance_cost_gbp", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Recent maintenance jobs")
st.dataframe(
    device_orders[
        [
            "event_id",
            "trust_code",
            "asset_id",
            "event_type",
            "priority",
            "work_order_status",
            "work_center",
            "planner_group",
            "event_reported_ts",
            "first_response_ts",
            "response_minutes",
            "work_order_age_days",
            "event_start_ts",
            "downtime_hours",
            "maintenance_cost_gbp",
            "failure_mode",
            "compliance_status",
            "next_inspection_due_date",
        ]
    ].sort_values("event_start_ts", ascending=False).head(30),
    use_container_width=True,
    hide_index=True,
)

st.info(
    "The key idea is simple: equipment problems spread outward. A machine fault becomes a technician task, then a waiting-time problem, then a workflow issue, and sometimes a patient-flow issue."
)
