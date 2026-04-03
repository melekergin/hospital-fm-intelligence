import os

import duckdb
import pandas as pd
import streamlit as st


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "hospital_fm.db")
REAL_METRICS_TABLE = "kpi_eric_real_trust_estate_metrics"
GLOSSARY_TERMS = {
    "Backlog": "Repair or upgrade work that still has not been done. It is hidden pressure building up in the estate.",
    "Trust": "An NHS organization that runs one or more hospitals or services.",
    "Estate": "The physical hospital environment: buildings, plant, rooms, utilities, and infrastructure.",
    "Planned Maintenance": "Work that is scheduled before something breaks, like routine servicing or inspection.",
    "Corrective Maintenance": "Work that happens after something goes wrong and needs repair.",
    "Compliance": "Whether inspections, checks, and standards are up to date.",
    "Work Order": "A maintenance job record that tells a team what needs to be done.",
    "Traceability": "Being able to prove where an item came from, where it went, and what happened to it.",
    "Reprocessing": "Running something through sterilisation again because it failed or was not released properly the first time.",
    "AEMP / ZSVA": "The hospital sterilisation area where instruments are cleaned, sterilised, tracked, and sent back for care.",
}


def apply_base_styles() -> None:
    st.markdown(
        """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Source+Sans+3:wght@400;600&display=swap');

        :root {
            --ink: #102432;
            --ink-soft: #37566a;
            --paper: #f7f3ea;
            --paper-2: #fffaf0;
            --teal: #0f766e;
            --teal-soft: #d8f0ec;
            --amber: #d97706;
            --amber-soft: #fff1d6;
            --coral: #b23a48;
            --navy: #102432;
            --line: rgba(16, 36, 50, 0.12);
            --shadow: 0 18px 40px rgba(16, 36, 50, 0.10);
        }

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(217, 119, 6, 0.18), transparent 26%),
                radial-gradient(circle at left 18%, rgba(15, 118, 110, 0.18), transparent 28%),
                radial-gradient(circle at bottom right, rgba(178, 58, 72, 0.10), transparent 22%),
                linear-gradient(180deg, #f7f3ea 0%, #efe6d7 100%);
            color: var(--ink);
        }

        html, body, [class*="css"] {
            font-family: 'Source Sans 3', sans-serif;
        }

        h1, h2, h3, h4 {
            font-family: 'Space Grotesk', sans-serif;
            color: var(--ink);
            letter-spacing: -0.02em;
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, rgba(16, 36, 50, 0.98) 0%, rgba(12, 60, 70, 0.98) 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.10);
        }

        [data-testid="stSidebar"] * {
            color: #f5efe5;
        }

        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] p {
            color: #f5efe5 !important;
        }

        [data-testid="stMetric"] {
            background: rgba(255, 250, 240, 0.78);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 0.55rem 0.75rem;
            box-shadow: 0 10px 24px rgba(16, 36, 50, 0.06);
        }

        .hero {
            background:
                linear-gradient(135deg, rgba(255, 250, 240, 0.90) 0%, rgba(216, 240, 236, 0.82) 100%);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1.6rem 1.8rem;
            box-shadow: var(--shadow);
        }

        .story-card {
            background: rgba(255, 250, 240, 0.88);
            border-left: 5px solid var(--amber);
            border-radius: 16px;
            padding: 1rem;
            min-height: 150px;
            border-top: 1px solid rgba(217, 119, 6, 0.16);
            box-shadow: 0 12px 30px rgba(16, 36, 50, 0.08);
        }

        .kpi-note {
            background: linear-gradient(135deg, rgba(216, 240, 236, 0.70), rgba(255, 250, 240, 0.92));
            border: 1px solid rgba(15, 118, 110, 0.12);
            border-radius: 14px;
            padding: 0.9rem 1rem;
            box-shadow: 0 8px 20px rgba(16, 36, 50, 0.05);
        }

        .nav-card {
            background:
                linear-gradient(145deg, rgba(255, 250, 240, 0.94) 0%, rgba(255, 241, 214, 0.82) 100%);
            border: 1px solid rgba(16, 36, 50, 0.10);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            min-height: 180px;
            box-shadow: var(--shadow);
        }

        .nav-card h3 {
            margin-bottom: 0.4rem;
            color: var(--ink);
        }

        .nav-card p {
            margin-bottom: 0.35rem;
            color: var(--ink-soft);
        }

        .section-label {
            font-size: 0.8rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--teal);
            font-weight: 700;
        }

        .stButton > button {
            background: linear-gradient(135deg, var(--teal) 0%, #155e75 100%);
            color: white;
            border: none;
            border-radius: 999px;
            padding: 0.45rem 1rem;
            font-weight: 700;
        }

        .stExpander {
            background: rgba(255, 250, 240, 0.78);
            border: 1px solid var(--line);
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(16, 36, 50, 0.05);
        }

        .stDataFrame, .stTable {
            border-radius: 14px;
            overflow: hidden;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


@st.cache_resource
def get_conn() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH, read_only=True)


@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    return get_conn().execute(sql).fetchdf()


def table_exists(table_name: str) -> bool:
    result = query(
        f"""
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_name = '{table_name}'
        """
    )
    return int(result.iloc[0, 0]) > 0


def pipeline_ready() -> bool:
    return os.path.exists(DB_PATH) and table_exists(REAL_METRICS_TABLE)


def render_setup_message() -> None:
    st.title("Hospital FM Intelligence Hub")
    st.markdown(
        """
        The dashboard is waiting for the DuckDB build.

        Run:

        ```powershell
        python scripts/normalize_eric_csv_encoding.py
        bruin run pipelines/
        streamlit run dashboard/app.py
        ```
        """
    )
    st.info(
        "The app uses the official ERIC site-data mart. Build the pipeline first if the pages are empty."
    )


def load_real_metrics() -> pd.DataFrame:
    return query(
        f"""
        SELECT *
        FROM {REAL_METRICS_TABLE}
        ORDER BY year_sort DESC, total_backlog_gbp DESC
        """
    )


def ordered_years(df: pd.DataFrame, *, descending: bool = True) -> list[str]:
    if "year_sort" in df.columns:
        year_frame = (
            df[["year", "year_sort"]]
            .drop_duplicates()
            .sort_values("year_sort", ascending=not descending)
        )
        return year_frame["year"].tolist()
    return sorted(df["year"].unique().tolist(), reverse=descending)


def filter_sidebar(df: pd.DataFrame, *, trust_limit: int | None = 25) -> tuple[list[str], list[str], list[str]]:
    years = ordered_years(df, descending=True)
    regions = sorted(df["region"].unique().tolist())
    trusts = sorted(df["trust_code"].unique().tolist())

    with st.sidebar:
        st.markdown("## Official ERIC View")
        selected_years = st.multiselect("Year", years, default=years)
        selected_regions = st.multiselect("Region", regions, default=regions)
        default_trusts = trusts[:trust_limit] if trust_limit and len(trusts) > trust_limit else trusts
        selected_trusts = st.multiselect("Trust", trusts, default=default_trusts)
        st.markdown("---")
        st.caption("Source: NHS ERIC site data")
        st.caption("Current official years: 2023/24 and 2024/25")
        st.caption("Normalization: per gross internal floor area (m2)")

    return selected_years, selected_regions, selected_trusts


def apply_filters(
    df: pd.DataFrame,
    selected_years: list[str],
    selected_regions: list[str],
    selected_trusts: list[str],
) -> pd.DataFrame:
    return df[
        df["year"].isin(selected_years)
        & df["region"].isin(selected_regions)
        & df["trust_code"].isin(selected_trusts)
    ].copy()


def render_glossary(term_names: list[str], *, title: str = "Quick Glossary") -> None:
    with st.expander(title, expanded=False):
        for term in term_names:
            explanation = GLOSSARY_TERMS.get(term)
            if explanation:
                st.markdown(f"**{term}**: {explanation}")


def render_how_to_read(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-note">
            <strong>{title}</strong><br>{body}
        </div>
        """,
        unsafe_allow_html=True,
    )
