import plotly.express as px
import streamlit as st

from lib import apply_base_styles, pipeline_ready, query, render_glossary, render_how_to_read, render_setup_message


st.set_page_config(
    page_title="Why Surgery Can Be Delayed By Sterile Instruments",
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

st.title(f"Why can surgery be delayed because of sterile instruments?")
st.write(
    "This page explains one of the hidden hospital dependencies that many people never see. If sterile sets are delayed, incomplete, untraceable, or need to be reprocessed, clinical work can slow down even when the operating team is ready."
)

render_glossary(
    ["AEMP / ZSVA", "Traceability", "Reprocessing"],
    title="Words You May Need On This Page",
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
    ("1. Dirty side", "Used instruments come back from care and enter decontamination."),
    ("2. Packing", "Sets are checked, assembled, wrapped, and linked to a batch."),
    ("3. Sterilisation", "Autoclaves run the cycle that makes the set ready again."),
    ("4. Release", "The set must be traceable, dispatched, and back with clinical teams on time."),
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

render_how_to_read(
    "What this page teaches",
    "AEMP is not just a technical service in the background. It is one of the reasons procedures can start on time, safely, and with the right instruments available.",
)

row1 = st.columns(2)

with row1[0]:
    st.subheader("How reliable is the sterile processing flow?")
    fig = px.bar(
        x=["Conformity", "Traceability", "Reprocess"],
        y=[
            trust_summary["conformity_rate_pct"],
            trust_summary["traceability_rate_pct"],
            trust_summary["reprocess_rate_pct"],
        ],
        labels={"x": "Process signal", "y": "Percent"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.55)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    render_how_to_read(
        "What to notice",
        "High conformity and high traceability are good. Reprocessing is the signal to watch: if it rises, throughput is being lost and delays become more likely.",
    )

with row1[1]:
    st.subheader("When is the workload heaviest?")
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
    render_how_to_read(
        "Why this matters",
        "If one shift carries much more work than the others, that is where delays, queues, and bottlenecks are more likely to appear.",
    )

st.subheader("Where does the process seem to slow down?")
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
    "The simple message is: if sterile processing slows down, care can slow down with it. This page is here to make that hidden dependency easier to understand."
)
