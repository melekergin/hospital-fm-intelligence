import plotly.express as px
import streamlit as st

from lib import apply_base_styles, apply_filters, filter_sidebar, load_real_metrics, pipeline_ready, render_setup_message


st.set_page_config(
    page_title="Estate Pressure",
    page_icon="📊",
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

st.title("Estate Pressure Explorer")
st.write(
    "This page is a trust-level comparison view built from official NHS ERIC site data. It is the analytic counterpart to the narrative home page."
)

col1, col2 = st.columns(2)

with col1:
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
            "gross_internal_floor_area_m2": "Gross internal floor area (m2)",
            "total_backlog_gbp": "Total backlog (GBP)",
            "backlog_risk_band_by_m2": "Risk band",
        },
    )
    fig_backlog.update_traces(textposition="top center")
    fig_backlog.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
    )
    st.plotly_chart(fig_backlog, use_container_width=True)

with col2:
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

st.subheader("Trend comparison")
trend_metric = st.radio(
    "Metric",
    ["backlog_cost_per_m2", "energy_cost_per_m2", "cleaning_cost_per_m2"],
    horizontal=True,
)

label_map = {
    "backlog_cost_per_m2": "Backlog per m2 (GBP)",
    "energy_cost_per_m2": "Energy per m2 (GBP)",
    "cleaning_cost_per_m2": "Cleaning per m2 (GBP)",
}

fig_trend = px.line(
    filtered,
    x="year",
    y=trend_metric,
    color="trust_code",
    markers=True,
    labels={"year": "Year", trend_metric: label_map[trend_metric], "trust_code": "Trust"},
)
fig_trend.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.55)",
)
st.plotly_chart(fig_trend, use_container_width=True)

st.subheader("Latest year ranking")
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
