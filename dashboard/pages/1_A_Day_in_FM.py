import streamlit as st

from lib import apply_base_styles, apply_filters, filter_sidebar, load_real_metrics, pipeline_ready, query, render_setup_message


st.set_page_config(
    page_title="A Day in FM",
    page_icon="🕒",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

df = load_real_metrics()
selected_years, selected_regions, selected_trusts = filter_sidebar(df, trust_limit=15)
filtered = apply_filters(df, selected_years, selected_regions, selected_trusts)

aemp = query(
    """
    SELECT *
    FROM kpi_aemp_process_summary
    ORDER BY cycle_count DESC
    """
)
aemp = aemp[
    aemp["year"].isin(selected_years)
    & aemp["region"].isin(selected_regions)
    & aemp["trust_code"].isin(selected_trusts)
].copy()

if filtered.empty:
    st.warning("No trusts match the current filters.")
    st.stop()

latest_year = filtered["year_sort"].max()
latest = filtered[filtered["year_sort"] == latest_year].copy()
latest_year_label = latest["year"].iloc[0]
aemp_latest = aemp[aemp["year"] == latest_year_label].copy() if not aemp.empty else aemp

st.title("A Day in the Life of Hospital FM")
st.write(
    "This page now links the official ERIC estate layer with two operational domains: maintenance and AEMP. It is the narrative entry point into how the hospital runs behind the scenes."
)

events = [
    (
        "6:30 AM",
        "Cleaning teams open the day",
        "Cleaning cost per m2 reflects how much effort the estate needs just to stay usable before clinics, wards, and theatres are fully active.",
        f"Current filtered average: GBP {latest['cleaning_cost_per_m2'].mean():,.2f} per m2",
    ),
    (
        "8:00 AM",
        "The estate starts consuming energy at scale",
        "Energy cost per m2 shows the underlying operational load of buildings, plant, and services that keep the hospital functioning.",
        f"Current filtered average: GBP {latest['energy_cost_per_m2'].mean():,.2f} per m2",
    ),
    (
        "11:00 AM",
        "AEMP releases sterile sets back to clinical teams",
        "Sterile processing turns technical throughput into patient-ready supply. Conformity and traceability show how reliable that hidden process really is.",
        (
            f"Current filtered average: {aemp_latest['conformity_rate_pct'].mean():,.2f}% conformity"
            if not aemp_latest.empty
            else "AEMP data not available in current filter"
        ),
    ),
    (
        "2:00 PM",
        "Backlog risk becomes a management issue",
        "Backlog per m2 shows how much unresolved estate work is sitting behind daily service delivery.",
        f"Current filtered average: GBP {latest['backlog_cost_per_m2'].mean():,.2f} per m2",
    ),
]

cols = st.columns(4)
for col, (time_label, title, body, metric) in zip(cols, events):
    col.markdown(
        f"""
        <div class="story-card">
            <h3>{time_label}</h3>
            <p><strong>{title}</strong></p>
            <p>{body}</p>
            <p><strong>{metric}</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")
st.subheader("What the day feels like by trust")

latest = latest.sort_values("total_backlog_gbp", ascending=False)

for _, row in latest.head(12).iterrows():
    st.markdown(
        f"""
        <div class="kpi-note">
            <strong>{row['trust_code']} · {row['trust_name']}</strong><br>
            Region: {row['region']}<br>
            Backlog: GBP {row['total_backlog_gbp']/1e6:,.1f}M |
            Energy: GBP {row['total_energy_cost_gbp']/1e6:,.1f}M |
            Cleaning: GBP {row['total_cleaning_cost_gbp']/1e6:,.1f}M<br>
            Estate pressure: backlog {row['backlog_cost_per_m2']:,.2f} per m2, energy {row['energy_cost_per_m2']:,.2f} per m2, cleaning {row['cleaning_cost_per_m2']:,.2f} per m2
        </div>
        """,
        unsafe_allow_html=True,
    )

if not aemp_latest.empty:
    st.subheader("AEMP signal in the same filtered view")
    st.dataframe(
        aemp_latest[
            [
                "trust_code",
                "trust_name",
                "cycle_count",
                "conformity_rate_pct",
                "traceability_rate_pct",
                "reprocess_rate_pct",
                "avg_dispatch_delay_minutes",
            ]
        ].sort_values("cycle_count", ascending=False).head(12),
        use_container_width=True,
        hide_index=True,
    )

st.info(
    "The story layer now spans estate, maintenance, and AEMP. The next step is to make the home page and trust cockpit feel like the same continuous user journey."
)
