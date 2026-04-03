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
    page_title="Why Backlog Becomes A Money Problem",
    page_icon="💷",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

estate = query(
    """
    SELECT *
    FROM kpi_eric_real_trust_estate_metrics
    ORDER BY year_sort DESC, total_backlog_gbp DESC
    """
)

years = ordered_years(estate, descending=True)
selected_year = st.sidebar.selectbox("Year", years, index=0)
year_view = estate[estate["year"] == selected_year].copy()
trust_options = year_view.sort_values("total_backlog_gbp", ascending=False)["trust_code"].tolist()
selected_trust = st.sidebar.selectbox("Trust", trust_options, index=0)

trust_row = year_view[year_view["trust_code"] == selected_trust].iloc[0]
trust_history = estate[estate["trust_code"] == selected_trust].sort_values("year_sort").copy()

st.title("Why does backlog become a money problem?")
st.write(
    "Backlog sounds abstract until you connect it to money. In hospital FM, backlog is not just a list of unfinished "
    "repairs. It is deferred spending, hidden financial pressure, and a sign that future fixes may become more expensive "
    "if they are left too long."
)

render_glossary(
    ["Backlog", "Estate", "Trust"],
    title="Words You May Need On This Page",
)
render_how_to_read(
    "How to use this page",
    "Start with the money story cards. Then compare the selected trust with its peers. The goal is to understand that "
    "finance in FM is not only about today's bills. It is also about the cost of waiting.",
)

money_cols = st.columns(4)
money_story = [
    (
        "Today's running cost",
        "Energy and cleaning are the visible bills that arrive now and have to be paid to keep the hospital functioning.",
        f"Energy + cleaning: GBP {(trust_row['total_energy_cost_gbp'] + trust_row['total_cleaning_cost_gbp'])/1e6:,.1f}M",
    ),
    (
        "Hidden future cost",
        "Backlog is money the estate still needs. It is not always paid this year, but the financial pressure still exists.",
        f"Backlog: GBP {trust_row['total_backlog_gbp']/1e6:,.1f}M",
    ),
    (
        "Where the risk sits",
        "Some backlog is low urgency. Some sits in higher-risk categories that are harder to ignore for long.",
        f"Risk band: {trust_row['backlog_risk_band_by_m2']}",
    ),
    (
        "Why waiting costs more",
        "Deferring estate work can mean more breakdowns, more disruption, and more expensive interventions later.",
        f"Backlog per m2: GBP {trust_row['backlog_cost_per_m2']:,.2f}",
    ),
]
for col, (title, body, metric) in zip(money_cols, money_story):
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

peer_chart = year_view.copy()
peer_chart["running_cost_gbp"] = peer_chart["total_energy_cost_gbp"] + peer_chart["total_cleaning_cost_gbp"]

row1 = st.columns(2)

with row1[0]:
    st.subheader("How does the selected trust compare with peers?")
    render_how_to_read(
        "How to read this bubble chart",
        "Further right means higher running cost today. Higher up means more hidden backlog waiting in the estate. Bigger bubbles mean a larger estate. Trusts in the upper-right are carrying both current cost pressure and deferred future cost.",
    )
    fig = px.scatter(
        peer_chart,
        x="running_cost_gbp",
        y="total_backlog_gbp",
        size="gross_internal_floor_area_m2",
        color="backlog_risk_band_by_m2",
        hover_name="trust_name",
        text="trust_code",
        color_discrete_map={
            "High": "#b23a48",
            "Significant": "#d17b0f",
            "Moderate": "#2c7da0",
            "Low": "#4b8f29",
        },
        labels={
            "running_cost_gbp": "Visible running cost: energy + cleaning (GBP)",
            "total_backlog_gbp": "Hidden future cost: backlog (GBP)",
            "backlog_risk_band_by_m2": "Backlog pressure",
        },
    )
    fig.update_traces(
        textposition="top center",
        marker_line_width=[3 if code == selected_trust else 0 for code in peer_chart["trust_code"]],
        marker_line_color="#13293d",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig, use_container_width=True)

with row1[1]:
    st.subheader("What is the cost mix for the selected trust?")
    render_how_to_read(
        "What to notice",
        "This is not a full budget. It is a simple FM money picture: visible running cost today versus the hidden backlog still waiting in the estate.",
    )
    cost_mix = pd.DataFrame(
        {
            "cost_type": ["Energy", "Cleaning", "Backlog"],
            "gbp": [
                trust_row["total_energy_cost_gbp"],
                trust_row["total_cleaning_cost_gbp"],
                trust_row["total_backlog_gbp"],
            ],
        }
    )
    fig = px.bar(
        cost_mix,
        x="cost_type",
        y="gbp",
        color="cost_type",
        color_discrete_map={
            "Energy": "#2c7da0",
            "Cleaning": "#4b8f29",
            "Backlog": "#b23a48",
        },
        labels={"cost_type": "Cost type", "gbp": "GBP"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Is the money pressure improving or getting worse over time?")
render_how_to_read(
    "How to read the trend",
    "If the backlog line rises, the trust is carrying more unresolved future cost into the next year. If energy and cleaning rise too, the trust may be under pressure on both current and deferred spending.",
)
trend_long = trust_history.melt(
    id_vars=["year", "year_sort"],
    value_vars=["total_backlog_gbp", "total_energy_cost_gbp", "total_cleaning_cost_gbp"],
    var_name="metric",
    value_name="gbp",
)
trend_long["metric"] = trend_long["metric"].map(
    {
        "total_backlog_gbp": "Backlog",
        "total_energy_cost_gbp": "Energy",
        "total_cleaning_cost_gbp": "Cleaning",
    }
)
fig = px.line(
    trend_long.sort_values("year_sort"),
    x="year",
    y="gbp",
    color="metric",
    markers=True,
    labels={"year": "Year", "gbp": "GBP", "metric": "FM cost signal"},
    category_orders={"year": ordered_years(trust_history, descending=False)},
    color_discrete_map={"Backlog": "#b23a48", "Energy": "#2c7da0", "Cleaning": "#4b8f29"},
)
fig.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.55)",
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Simple finance interpretation")
interpretation_cols = st.columns(3)
interpretations = [
    (
        "If backlog is high",
        "The estate is carrying a large bill into the future, even if that bill is not being paid immediately.",
    ),
    (
        "If running costs are high",
        "The hospital is already spending heavily to keep the estate operating day to day.",
    ),
    (
        "If both are high",
        "That is the hardest position: expensive to run now, and expensive to fix later.",
    ),
]
for col, (title, body) in zip(interpretation_cols, interpretations):
    col.markdown(
        f"""
        <div class="story-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("Selected trust finance view")
st.dataframe(
    pd.DataFrame(
        [
            {
                "trust_code": trust_row["trust_code"],
                "trust_name": trust_row["trust_name"],
                "region": trust_row["region"],
                "site_count": trust_row["site_count"],
                "gross_internal_floor_area_m2": trust_row["gross_internal_floor_area_m2"],
                "total_backlog_gbp": trust_row["total_backlog_gbp"],
                "total_energy_cost_gbp": trust_row["total_energy_cost_gbp"],
                "total_cleaning_cost_gbp": trust_row["total_cleaning_cost_gbp"],
                "backlog_cost_per_m2": trust_row["backlog_cost_per_m2"],
                "energy_cost_per_m2": trust_row["energy_cost_per_m2"],
                "cleaning_cost_per_m2": trust_row["cleaning_cost_per_m2"],
                "backlog_risk_band_by_m2": trust_row["backlog_risk_band_by_m2"],
            }
        ]
    ),
    use_container_width=True,
    hide_index=True,
)

st.info(
    "This page does not try to model the full hospital budget. It focuses on one FM lesson: backlog is a financial story as much as a technical one."
)
