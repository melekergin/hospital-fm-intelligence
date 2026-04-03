import plotly.express as px
import streamlit as st

from lib import apply_base_styles, apply_filters, filter_sidebar, load_real_metrics, pipeline_ready, query, render_setup_message


st.set_page_config(
    page_title="Equipment Journey",
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
work_orders = query("SELECT * FROM fact_equipment_work_orders ORDER BY event_start_ts DESC")

for frame in (reliability, compliance, work_order_flow, work_orders):
    frame = frame

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

st.title("Equipment Journey")
st.write(
    "This page now shows both equipment reliability and the workflow around maintenance. The synthetic layer is anchored to real ERIC trust scale, but the operational event flow is intentionally SAP-like rather than copied from a live system."
)

device = st.selectbox(
    "Choose equipment category",
    sorted(reliability_latest["equipment_category"].unique().tolist()),
)

device_reliability = reliability_latest[reliability_latest["equipment_category"] == device].copy()
device_compliance = compliance_latest[compliance_latest["equipment_category"] == device].copy()
device_flow = flow_latest[flow_latest["equipment_category"] == device].copy()
device_orders = orders_latest[orders_latest["equipment_category"] == device].copy()

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

metric_cols = st.columns(5)
metric_cols[0].metric("Assets in view", f"{int(device_reliability['asset_count'].sum())}")
metric_cols[1].metric("Corrective events", f"{int(device_reliability['corrective_events'].sum())}")
metric_cols[2].metric("Overdue inspections", f"{int(device_compliance['overdue_assets'].sum())}")
metric_cols[3].metric("Action required", f"{int(device_compliance['action_required_assets'].sum())}")
metric_cols[4].metric("Avg availability", f"{device_reliability['availability_pct'].mean():.2f}%")

story_cols = st.columns(5)
steps = [
    ("1. Install", "Assets are registered against trust and site context."),
    ("2. Inspect", "Inspection dates determine whether compliance is still in date."),
    ("3. Notify", "A maintenance event begins as a notification or planning item."),
    ("4. Execute", "Orders move through planning, approval, and in-progress states."),
    ("5. Close", "Downtime, cost, and compliance become measurable outcomes."),
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

row1 = st.columns(2)

with row1[0]:
    fig = px.scatter(
        merged,
        x="backlog_cost_per_m2",
        y="failure_rate_per_asset",
        size="asset_count",
        color="compliance_rate_pct",
        hover_name="trust_name",
        text="trust_code",
        labels={
            "backlog_cost_per_m2": "Backlog per m2 (GBP)",
            "failure_rate_per_asset": "Failure rate per asset",
            "compliance_rate_pct": "Compliance %",
        },
        color_continuous_scale=["#b23a48", "#d17b0f", "#2c7da0", "#4b8f29"],
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig, use_container_width=True)

with row1[1]:
    status_order = ["Notification", "Planning", "Approved", "In Progress", "Technically Complete", "Closed"]
    flow_chart = px.bar(
        device_flow,
        x="work_order_status",
        y="order_count",
        color="event_type",
        category_orders={"work_order_status": status_order},
        labels={
            "work_order_status": "Work-order status",
            "order_count": "Order count",
            "event_type": "Event type",
        },
    )
    flow_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(flow_chart, use_container_width=True)

row2 = st.columns(2)

with row2[0]:
    compliance_chart = px.bar(
        device_compliance.sort_values("overdue_assets", ascending=False).head(12),
        x="trust_code",
        y=["overdue_assets", "action_required_assets"],
        barmode="group",
        labels={
            "value": "Asset count",
            "trust_code": "Trust",
            "variable": "Compliance issue",
        },
    )
    compliance_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(compliance_chart, use_container_width=True)

with row2[1]:
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

st.subheader(f"{device} trust view")
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
            "backlog_cost_per_m2",
            "energy_cost_per_m2",
            "cleaning_cost_per_m2",
        ]
    ].sort_values("maintenance_cost_gbp", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Recent work orders")
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
    "The maintenance layer now includes synthetic workflow state and compliance due dates. The next strong addition would be a trust-specific asset drilldown page or a DGUV/STK-style compliance page."
)
