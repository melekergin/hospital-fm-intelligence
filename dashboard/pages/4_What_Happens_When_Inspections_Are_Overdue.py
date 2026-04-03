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
    page_title="What Happens When Inspections Are Overdue?",
    page_icon="🛡️",
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

assets = query(
    """
    SELECT *
    FROM fact_equipment_compliance_assets
    ORDER BY compliance_risk_rank, days_from_due_date DESC
    """
)
summary = query(
    """
    SELECT *
    FROM kpi_equipment_compliance
    ORDER BY overdue_assets DESC, action_required_assets DESC
    """
)

assets = assets[
    assets["year"].isin(selected_years)
    & assets["region"].isin(selected_regions)
    & assets["trust_code"].isin(selected_trusts)
].copy()
summary = summary[
    summary["year"].isin(selected_years)
    & summary["region"].isin(selected_regions)
    & summary["trust_code"].isin(selected_trusts)
].copy()

if assets.empty or summary.empty:
    st.warning("No compliance data matches the current filters.")
    st.stop()

latest_year_label = estate_filtered[estate_filtered["year_sort"] == estate_filtered["year_sort"].max()]["year"].iloc[0]
assets_latest = assets[assets["year"] == latest_year_label].copy()
summary_latest = summary[summary["year"] == latest_year_label].copy()

st.title("What happens when inspections are overdue?")
st.write(
    "This page is about a common hidden problem. Nothing may look broken yet, but inspections are late, risk is rising, and the hospital is carrying more uncertainty than it should."
)

render_glossary(
    ["Compliance", "Work Order", "Planned Maintenance", "Corrective Maintenance"],
    title="Words You May Need On This Page",
)

device = st.selectbox(
    "Choose equipment type",
    sorted(assets_latest["equipment_category"].unique().tolist()),
)

device_assets = assets_latest[assets_latest["equipment_category"] == device].copy()
device_summary = summary_latest[summary_latest["equipment_category"] == device].copy()

metric_cols = st.columns(5)
metric_cols[0].metric("Assets in view", f"{len(device_assets)}")
metric_cols[1].metric("In date", f"{int((device_assets['compliance_status'] == 'In Date').sum())}")
metric_cols[2].metric("Due soon", f"{int((device_assets['compliance_risk_bucket'] == 'Due Soon').sum())}")
metric_cols[3].metric("Overdue", f"{int(device_summary['overdue_assets'].sum())}")
metric_cols[4].metric("Action required", f"{int(device_summary['action_required_assets'].sum())}")

story_cols = st.columns(4)
steps = [
    ("1. Inspect", "A device should be checked before it becomes risky."),
    ("2. Miss the date", "If the due date passes, uncertainty starts growing."),
    ("3. Risk increases", "Some issues stay overdue, others become serious enough to require action."),
    ("4. Pressure spreads", "The hospital now carries more operational risk even if no visible failure has happened yet."),
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
    "Compliance is not just paperwork. It is a way of reducing uncertainty before a failure becomes visible to staff or patients.",
)

row1 = st.columns(2)

with row1[0]:
    st.subheader("How many assets are drifting into risk?")
    risk_counts = (
        device_assets.groupby("compliance_risk_bucket", as_index=False)
        .size()
        .rename(columns={"size": "asset_count"})
    )
    bucket_order = ["Action Required", "Critical Overdue", "Overdue", "Due Soon", "In Date"]
    risk_chart = px.bar(
        risk_counts,
        x="compliance_risk_bucket",
        y="asset_count",
        category_orders={"compliance_risk_bucket": bucket_order},
        color="compliance_risk_bucket",
        color_discrete_map={
            "Action Required": "#8c1c13",
            "Critical Overdue": "#b23a48",
            "Overdue": "#d17b0f",
            "Due Soon": "#2c7da0",
            "In Date": "#4b8f29",
        },
        labels={"compliance_risk_bucket": "Inspection risk level", "asset_count": "Assets"},
    )
    risk_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(risk_chart, use_container_width=True)
    render_how_to_read(
        "What to notice",
        "Green means the inspection position is healthy. Blue means the hospital should pay attention soon. Orange and red mean risk is already building up.",
    )

with row1[1]:
    st.subheader("Which trusts have the biggest inspection problem?")
    trust_chart = px.bar(
        device_summary.sort_values(["overdue_assets", "action_required_assets"], ascending=False).head(12),
        x="trust_code",
        y=["overdue_assets", "action_required_assets"],
        barmode="group",
        labels={
            "trust_code": "Trust",
            "value": "Assets",
            "variable": "Issue type",
        },
    )
    trust_chart.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(trust_chart, use_container_width=True)
    render_how_to_read(
        "Why this matters",
        "A tall bar means more of that equipment type is sitting in a worse inspection position. That does not guarantee immediate failure, but it does mean the trust is carrying more avoidable risk.",
    )

st.subheader("Which specific assets look most exposed?")
asset_risk_view = device_assets.sort_values(
    ["compliance_risk_rank", "days_from_due_date"],
    ascending=[True, False],
)
st.dataframe(
    asset_risk_view[
        [
            "trust_code",
            "asset_id",
            "site_code",
            "criticality",
            "inspection_outcome",
            "compliance_status",
            "compliance_risk_bucket",
            "days_from_due_date",
            "last_inspection_date",
            "next_inspection_due_date",
            "acquisition_value_gbp",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)

st.info(
    "The simple message is: overdue inspections are early warning signals. The hospital wants to act here before the problem becomes a breakdown, cancellation, or safety issue."
)
