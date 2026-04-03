import plotly.express as px
import streamlit as st

from lib import (
    apply_base_styles,
    apply_filters,
    filter_sidebar,
    load_real_metrics,
    ordered_years,
    pipeline_ready,
    render_glossary,
    render_how_to_read,
    render_setup_message,
)


st.set_page_config(
    page_title="Why Buildings Matter",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

df = load_real_metrics()
selected_years, selected_regions, selected_trusts = filter_sidebar(df, trust_limit=40)
filtered = apply_filters(df, selected_years, selected_regions, selected_trusts)

if filtered.empty:
    st.warning("No trusts match the current filters.")
    st.stop()

latest_year = filtered["year_sort"].max()
latest = filtered[filtered["year_sort"] == latest_year].copy()

st.title("Why hidden building pressure becomes patient pressure")
st.write(
    "Patients mostly see wards, waiting areas, and treatment rooms. Behind that, hospital FM teams deal with "
    "aging buildings, energy costs, cleaning demand, and unresolved repairs. This page helps explain why "
    "problems in the estate eventually show up as operational problems."
)

render_glossary(["Estate", "Backlog", "Trust"], title="Hospital FM Words, Explained Simply")
render_how_to_read(
    "How to use this page",
    "Start with the two comparison charts to see which trusts carry heavier building pressure. Then use the "
    "trend view to see whether that pressure is rising or stabilising over time.",
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Which trusts carry the heaviest repair burden?")
    render_how_to_read(
        "What this chart shows",
        "Each point is one trust. Farther right means a larger estate. Higher up means more unresolved backlog. "
        "Bigger circles also mean higher energy spend. Trusts in the upper-right area are carrying the heaviest "
        "overall building pressure.",
    )
    fig_backlog = px.scatter(
        latest,
        x="gross_internal_floor_area_m2",
        y="total_backlog_gbp",
        size="total_energy_cost_gbp",
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
            "gross_internal_floor_area_m2": "Hospital estate size (m2)",
            "total_backlog_gbp": "Unresolved building backlog (GBP)",
            "backlog_risk_band_by_m2": "Pressure band",
        },
    )
    fig_backlog.update_traces(textposition="top center")
    fig_backlog.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig_backlog, use_container_width=True)

with col2:
    st.subheader("Which trusts spend more to keep the estate running?")
    render_how_to_read(
        "What to notice",
        "Trusts higher up spend more on cleaning for each square metre. Trusts farther right spend more on energy "
        "for each square metre. A trust high on both axes may be dealing with an expensive estate to operate day to day.",
    )
    fig_cleaning = px.scatter(
        latest,
        x="energy_cost_per_m2",
        y="cleaning_cost_per_m2",
        size="gross_internal_floor_area_m2",
        color="region",
        hover_name="trust_name",
        text="trust_code",
        labels={
            "energy_cost_per_m2": "Energy cost per m2 (GBP)",
            "cleaning_cost_per_m2": "Cleaning cost per m2 (GBP)",
            "region": "Region",
        },
    )
    fig_cleaning.update_traces(textposition="top center")
    fig_cleaning.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig_cleaning, use_container_width=True)

st.subheader("Is pressure building up over time?")
trend_metric = st.radio(
    "Choose one estate signal to follow over time",
    ["backlog_cost_per_m2", "energy_cost_per_m2", "cleaning_cost_per_m2"],
    horizontal=True,
)

label_map = {
    "backlog_cost_per_m2": "Backlog per m2 (GBP)",
    "energy_cost_per_m2": "Energy per m2 (GBP)",
    "cleaning_cost_per_m2": "Cleaning per m2 (GBP)",
}

render_how_to_read(
    "How to read the trend",
    "If a line rises, pressure is getting worse for that trust in the selected measure. Backlog tells you about "
    "unfinished repair burden. Energy and cleaning show how expensive the estate is to keep running.",
)

fig_trend = px.line(
    filtered.sort_values("year_sort"),
    x="year",
    y=trend_metric,
    color="trust_code",
    markers=True,
    labels={"year": "Year", trend_metric: label_map[trend_metric], "trust_code": "Trust"},
    category_orders={"year": ordered_years(filtered, descending=False)},
)
fig_trend.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.55)",
)
st.plotly_chart(fig_trend, use_container_width=True)

st.subheader("Which trusts stand out most in the latest year?")
ranking_metric = st.selectbox(
    "Rank trusts by",
    [
        "total_backlog_gbp",
        "backlog_cost_per_m2",
        "total_energy_cost_gbp",
        "energy_cost_per_m2",
        "total_cleaning_cost_gbp",
        "cleaning_cost_per_m2",
    ],
)

render_how_to_read(
    "Why this matters",
    "This ranking is a simple way to spot which trusts may need closer attention. High total values often reflect "
    "large estates. High per-m2 values suggest pressure that stays high even after adjusting for estate size.",
)

st.dataframe(
    latest.sort_values(ranking_metric, ascending=False)[
        [
            "trust_code",
            "trust_name",
            "region",
            "site_count",
            "gross_internal_floor_area_m2",
            "total_backlog_gbp",
            "backlog_cost_per_m2",
            "total_energy_cost_gbp",
            "energy_cost_per_m2",
            "total_cleaning_cost_gbp",
            "cleaning_cost_per_m2",
            "backlog_risk_band_by_m2",
        ]
    ],
    use_container_width=True,
    hide_index=True,
)
