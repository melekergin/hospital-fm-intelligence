import plotly.express as px
import streamlit as st

from lib import apply_base_styles, pipeline_ready, query, render_setup_message


st.set_page_config(
    page_title="AEMP Process",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

summary = query(
    """
    SELECT *
    FROM kpi_aemp_process_summary
    ORDER BY cycle_count DESC
    """
)
shift_load = query(
    """
    SELECT *
    FROM kpi_aemp_shift_load
    ORDER BY cycle_count DESC
    """
)

if summary.empty:
    st.warning("AEMP data is not available yet. Generate the synthetic AEMP files and rerun the pipeline.")
    st.stop()

trust_options = summary.sort_values("cycle_count", ascending=False)["trust_code"].tolist()
selected_trust = st.sidebar.selectbox("Trust", trust_options, index=0)

trust_summary = summary[summary["trust_code"] == selected_trust].iloc[0]
trust_shift = shift_load[shift_load["trust_code"] == selected_trust].copy()

st.title(f"AEMP / ZSVA Process Explorer: {trust_summary['trust_name']}")
st.write(
    "This page is the first sterile processing domain view. It turns synthetic cycle and batch data into a process story around conformity, traceability, reprocessing, and shift load."
)

metric_cols = st.columns(6)
metric_cols[0].metric("Cycles", f"{int(trust_summary['cycle_count'])}")
metric_cols[1].metric("Autoclaves", f"{int(trust_summary['autoclave_count'])}")
metric_cols[2].metric("Conformity", f"{trust_summary['conformity_rate_pct']:.2f}%")
metric_cols[3].metric("Traceability", f"{trust_summary['traceability_rate_pct']:.2f}%")
metric_cols[4].metric("Reprocess rate", f"{trust_summary['reprocess_rate_pct']:.2f}%")
metric_cols[5].metric("Batches", f"{int(trust_summary['batch_count'])}")

story_cols = st.columns(4)
cards = [
    ("1. Decontamination", "Used instruments enter the dirty side and are prepared for processing."),
    ("2. Packing", "Sets are assembled, wrapped, and linked to a batch path."),
    ("3. Sterilisation", "Autoclave cycles run with measurable duration and conformity."),
    ("4. Dispatch", "Batches are released with traceability and dispatch delay."),
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
    fig = px.bar(
        x=["Conformity", "Traceability", "Reprocess"],
        y=[
            trust_summary["conformity_rate_pct"],
            trust_summary["traceability_rate_pct"],
            trust_summary["reprocess_rate_pct"],
        ],
        labels={"x": "Metric", "y": "Percent"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with row1[1]:
    fig = px.bar(
        trust_shift.groupby("shift_name", as_index=False)["cycle_count"].sum(),
        x="shift_name",
        y="cycle_count",
        labels={"shift_name": "Shift", "cycle_count": "Cycles"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Shift and bottleneck profile")
st.dataframe(
    trust_shift[
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
    "The AEMP layer is synthetic, but it now gives the project a second operational domain beyond maintenance. The next sensible step is to connect AEMP into the day-in-the-life page and trust cockpit."
)
