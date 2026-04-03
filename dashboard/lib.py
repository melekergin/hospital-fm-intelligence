import os

import duckdb
import pandas as pd
import streamlit as st


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "hospital_fm.db")
REAL_METRICS_TABLE = "kpi_eric_real_trust_estate_metrics"


def apply_base_styles() -> None:
    st.markdown(
        """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Source+Sans+3:wght@400;600&display=swap');

        .stApp {
            background:
                radial-gradient(circle at top right, rgba(236, 201, 75, 0.18), transparent 28%),
                radial-gradient(circle at left 20%, rgba(44, 125, 160, 0.16), transparent 32%),
                linear-gradient(180deg, #f4efe3 0%, #ebe4d6 100%);
            color: #1f2933;
        }

        html, body, [class*="css"] {
            font-family: 'Source Sans 3', sans-serif;
        }

        h1, h2, h3, h4 {
            font-family: 'Space Grotesk', sans-serif;
            color: #13293d;
        }

        [data-testid="stSidebar"] {
            background: rgba(19, 41, 61, 0.96);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: #f3efe6;
        }

        .hero {
            background: rgba(255, 252, 245, 0.72);
            border: 1px solid rgba(19, 41, 61, 0.08);
            border-radius: 20px;
            padding: 1.6rem 1.8rem;
            box-shadow: 0 18px 50px rgba(19, 41, 61, 0.08);
        }

        .story-card {
            background: rgba(255, 252, 245, 0.78);
            border-left: 5px solid #d17b0f;
            border-radius: 16px;
            padding: 1rem;
            min-height: 150px;
            box-shadow: 0 12px 36px rgba(19, 41, 61, 0.08);
        }

        .kpi-note {
            background: rgba(19, 41, 61, 0.06);
            border-radius: 14px;
            padding: 0.9rem 1rem;
        }

        .nav-card {
            background: rgba(255, 252, 245, 0.86);
            border: 1px solid rgba(19, 41, 61, 0.08);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            min-height: 180px;
            box-shadow: 0 14px 32px rgba(19, 41, 61, 0.08);
        }

        .nav-card h3 {
            margin-bottom: 0.4rem;
        }

        .nav-card p {
            margin-bottom: 0.35rem;
        }

        .section-label {
            font-size: 0.8rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #8c6d46;
            font-weight: 700;
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


def filter_sidebar(df: pd.DataFrame, *, trust_limit: int | None = 25) -> tuple[list[str], list[str], list[str]]:
    years = sorted(df["year"].unique().tolist(), reverse=True)
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
