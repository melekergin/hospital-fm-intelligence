import streamlit as st

from lib import (
    apply_base_styles,
    apply_filters,
    filter_sidebar,
    load_real_metrics,
    ordered_years,
    pipeline_ready,
    query,
    render_glossary,
    render_setup_message,
)


st.set_page_config(
    page_title="Start Here",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_styles()

if not pipeline_ready():
    render_setup_message()
    st.stop()

summary = load_real_metrics()
selected_years, selected_regions, selected_trusts = filter_sidebar(summary)
filtered = apply_filters(summary, selected_years, selected_regions, selected_trusts)

if filtered.empty:
    st.warning("No trusts match the current filters.")
    st.stop()

latest_year = filtered["year_sort"].max()
latest = filtered[filtered["year_sort"] == latest_year].copy()

st.title("Start here")
st.write(
    "Choose the hospital question or role that feels most interesting to you. This page is only here to help you enter the learning journey quickly."
)

render_glossary(
    ["Trust", "Estate", "Backlog", "Compliance", "AEMP / ZSVA"],
    title="FM Words Explained Simply",
)

st.markdown("### Choose a path")
st.caption("Start with a hospital problem, not a dashboard.")

routes = [
    (
        "A day in hospital FM",
        "pages/1_A_Day_In_Hospital_FM.py",
        "Guided story of one day behind the scenes.",
        "Follow one hospital day from early cleaning and bed turnover to backlog pressure by the afternoon.",
    ),
    (
        "Why is there no bed?",
        "pages/7_Why_No_Bed_For_A_New_Patient.py",
        "Patient-flow scenario with bed readiness and hidden blockers.",
        "Go straight to the most intuitive patient-flow question.",
    ),
    (
        "What if equipment fails?",
        "pages/8_What_Happens_When_A_CT_Scanner_Fails.py",
        "Concrete device failure scenario.",
        "Follow a CT scanner problem from fault to operational impact.",
    ),
    (
        "Where does the money go?",
        "pages/9_Why_Backlog_Becomes_A_Money_Problem.py",
        "Finance view through backlog and estate cost.",
        "See why backlog is a money problem, not only a maintenance problem.",
    ),
]
for index in range(0, len(routes), 2):
    route_cols = st.columns(2)
    for col, (title, page, help_text, body) in zip(route_cols, routes[index : index + 2]):
        with col:
            col.markdown(
                f"""
                <div class="nav-card">
                    <h3>{title}</h3>
                    <p>{body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.page_link(page, label="Open this path", help=help_text)
