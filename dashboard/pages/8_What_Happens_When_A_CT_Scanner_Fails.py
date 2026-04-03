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
    page_title="What Happens When A CT Scanner Fails?",
    page_icon="🩻",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

reliability = query(
    """
    SELECT *
    FROM kpi_equipment_reliability
    WHERE equipment_category = 'CT Scanner'
    ORDER BY maintenance_cost_gbp DESC
    """
)
compliance = query(
    """
    SELECT *
    FROM kpi_equipment_compliance
    WHERE equipment_category = 'CT Scanner'
    ORDER BY overdue_assets DESC, action_required_assets DESC
    """
)
flow = query(
    """
    SELECT *
    FROM kpi_work_order_flow
    WHERE equipment_category = 'CT Scanner'
    ORDER BY total_order_cost_gbp DESC
    """
)
aging = query(
    """
    SELECT *
    FROM kpi_work_order_aging
    WHERE equipment_category = 'CT Scanner'
    ORDER BY order_count DESC
    """
)
orders = query(
    """
    SELECT *
    FROM fact_equipment_work_orders
    WHERE equipment_category = 'CT Scanner'
    ORDER BY event_start_ts DESC
    """
)

if reliability.empty:
    st.warning("No CT scanner data is available in the current build.")
    st.stop()

years = ordered_years(reliability, descending=True)
selected_year = st.sidebar.selectbox("Year", years, index=0)
year_reliability = reliability[reliability["year"] == selected_year].copy()
year_compliance = compliance[compliance["year"] == selected_year].copy()
year_flow = flow[flow["year"] == selected_year].copy()
year_aging = aging[aging["year"] == selected_year].copy()
year_orders = orders[orders["year"] == selected_year].copy()
trust_options = year_reliability.sort_values("downtime_hours", ascending=False)["trust_code"].tolist()
selected_trust = st.sidebar.selectbox("Trust", trust_options, index=0)

trust_reliability = year_reliability[year_reliability["trust_code"] == selected_trust].iloc[0]
trust_compliance = year_compliance[year_compliance["trust_code"] == selected_trust]
trust_flow = year_flow[year_flow["trust_code"] == selected_trust].copy()
trust_aging = year_aging[year_aging["trust_code"] == selected_trust].copy()
trust_orders = year_orders[year_orders["trust_code"] == selected_trust].copy()

overdue_assets = int(trust_compliance["overdue_assets"].sum()) if not trust_compliance.empty else 0
action_required_assets = int(trust_compliance["action_required_assets"].sum()) if not trust_compliance.empty else 0

st.title("What happens when a CT scanner fails?")
st.write(
    "This is a useful hospital FM scenario because everyone immediately understands the visible impact: diagnostics "
    "slow down, appointments may be delayed, staff must escalate, and the problem quickly becomes operational, not "
    "just technical."
)

render_glossary(
    ["Work Order", "Planned Maintenance", "Corrective Maintenance", "Compliance"],
    title="Words You May Need On This Page",
)
render_how_to_read(
    "How to use this page",
    "Follow the scanner journey from normal service into failure and response. The charts below show whether the trust "
    "is dealing mostly with breakdowns, overdue inspections, slow workflow, or expensive downtime.",
)

avg_response = trust_flow["avg_response_minutes"].mean() if not trust_flow.empty else 0
sla_met = trust_flow["response_sla_met_pct"].mean() if not trust_flow.empty else 0

metric_cols = st.columns(8)
metric_cols[0].metric("CT scanners", f"{int(trust_reliability['asset_count'])}")
metric_cols[1].metric("Breakdowns", f"{int(trust_reliability['corrective_events'])}")
metric_cols[2].metric("Downtime", f"{trust_reliability['downtime_hours']:,.1f} hrs")
metric_cols[3].metric("Availability", f"{trust_reliability['availability_pct']:.2f}%")
metric_cols[4].metric("Overdue inspections", f"{overdue_assets}")
metric_cols[5].metric("Action required", f"{action_required_assets}")
metric_cols[6].metric("Avg response", f"{avg_response:.0f} min")
metric_cols[7].metric("SLA met", f"{sla_met:.1f}%")

journey_cols = st.columns(5)
journey_steps = [
    ("1. Installed", "The scanner enters the hospital, is registered, and becomes part of the asset base."),
    ("2. In clinical use", "It supports diagnostics and patient decisions day after day."),
    ("3. Error or due service", "The scanner either fails unexpectedly or reaches a maintenance milestone."),
    ("4. Technician response", "A work order is raised so engineers can inspect, repair, or escalate."),
    ("5. Back in service or delayed", "If the fix takes time, appointments and patient flow can be disrupted."),
]
for col, (title, body) in zip(journey_cols, journey_steps):
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
    st.subheader("Which trusts look most exposed on CT scanners?")
    render_how_to_read(
        "What to notice",
        "Higher dots mean more CT scanner failures per asset. Larger bubbles mean more scanner downtime. Dots in warmer colours have lower availability. Those are the trusts where CT disruption may be felt more sharply.",
    )
    fig = px.scatter(
        year_reliability,
        x="failure_rate_per_asset",
        y="downtime_hours",
        size="asset_count",
        color="availability_pct",
        hover_name="trust_name",
        text="trust_code",
        color_continuous_scale=["#b23a48", "#d17b0f", "#2c7da0", "#4b8f29"],
        labels={
            "failure_rate_per_asset": "Scanner failures per asset",
            "downtime_hours": "Downtime hours",
            "availability_pct": "Availability %",
        },
    )
    fig.update_traces(
        textposition="top center",
        marker_line_width=[3 if code == selected_trust else 0 for code in year_reliability["trust_code"]],
        marker_line_color="#13293d",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig, use_container_width=True)

with row1[1]:
    st.subheader("Where do CT maintenance jobs sit in the process?")
    render_how_to_read(
        "How to read this",
        "This chart shows the CT-related maintenance queue for the selected trust. If many jobs remain in notification, planning, or in progress, recovery from scanner issues may be moving slowly.",
    )
    status_order = ["Notification", "Planning", "Approved", "In Progress", "Technically Complete", "Closed"]
    if not trust_flow.empty:
        fig = px.bar(
            trust_flow,
            x="work_order_status",
            y="order_count",
            color="event_type",
            category_orders={"work_order_status": status_order},
            labels={
                "work_order_status": "Work-order stage",
                "order_count": "Maintenance jobs",
                "event_type": "Job type",
            },
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.55)",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No CT workflow data is available for the selected trust and year.")

row2 = st.columns(2)

with row2[0]:
    st.subheader("Is this trust mostly dealing with planned work or breakdowns?")
    render_how_to_read(
        "Why this matters",
        "Planned work is expected and can usually be scheduled. Corrective work is more disruptive because it follows a problem or failure. A high corrective share usually means more operational disruption.",
    )
    fig = px.bar(
        x=["Planned maintenance", "Breakdowns"],
        y=[trust_reliability["planned_events"], trust_reliability["corrective_events"]],
        labels={"x": "Type of CT maintenance activity", "y": "Events"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with row2[1]:
    st.subheader("What is the inspection picture for CT scanners?")
    render_how_to_read(
        "What to notice",
        "Overdue inspections and action-required findings increase uncertainty around readiness and risk. They do not always mean immediate failure, but they make confident operation harder.",
    )
    fig = px.bar(
        x=["Overdue inspections", "Action required"],
        y=[overdue_assets, action_required_assets],
        labels={"x": "Inspection signal", "y": "Count"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

row3 = st.columns(2)

with row3[0]:
    st.subheader("How long does response take after the fault is reported?")
    render_how_to_read(
        "Why this matters",
        "A scanner can fail quickly, but the real operational question is how fast the response begins. Slower response means more waiting before recovery even starts.",
    )
    if not trust_flow.empty:
        response_view = trust_flow.groupby("work_order_status", as_index=False)["avg_response_minutes"].mean()
        fig = px.bar(
            response_view,
            x="work_order_status",
            y="avg_response_minutes",
            category_orders={"work_order_status": status_order},
            labels={
                "work_order_status": "Work-order stage",
                "avg_response_minutes": "Average response time (minutes)",
            },
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(255,255,255,0.55)",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No CT response-time data is available for the selected trust and year.")

with row3[1]:
    st.subheader("How old is the CT maintenance queue?")
    render_how_to_read(
        "How to read this",
        "This shows how long CT-related work orders stay open or took to resolve. If many sit in older buckets, the queue is aging and the scanner problem may linger operationally.",
    )
    if not trust_aging.empty:
        bucket_order = ["Under 1 day", "1-3 days", "3-7 days", "1-2 weeks", "Over 2 weeks"]
        aging_rollup = trust_aging.groupby("work_order_age_bucket", as_index=False)["order_count"].sum()
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
        st.info("No CT aging data is available for the selected trust and year.")

st.subheader("Recent CT scanner work orders")
st.dataframe(
    trust_orders[
        [
            "event_id",
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
    ].sort_values("event_start_ts", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.info(
    "A CT scanner fault is a good example of how hospital FM becomes visible. The issue starts as an asset problem, "
    "but it quickly becomes a workflow, scheduling, and patient-care problem."
)
