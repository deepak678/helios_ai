import json
import sys
from pathlib import Path

import plotly.express as px
import requests
import streamlit as st

# Ensure the project root is on sys.path when Streamlit launches from the ui folder
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from app.routes.analyze import analyze_issues
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "Cannot import app.routes.analyze. Make sure you run Streamlit from the project root "
        "and that the repository contains the app package with __init__.py files."
    ) from exc

API_URL = "http://localhost:8000/analyze"
HEALTH_URL = "http://localhost:8000/health"

CLUSTER_THEME_NAMES = {
    0: "Payments & Approvals",
    1: "Controls & Segregation",
    2: "Reconciliation & Systems",
    3: "Reporting & Data Quality",
}


def call_backend():
    try:
        response = requests.post(API_URL, timeout=10)
        response.raise_for_status()
        return response.json(), "backend"
    except Exception:
        return None, None


def fetch_analysis():
    backend_data, source = call_backend()
    if backend_data is not None:
        return backend_data, source

    analysis = analyze_issues()
    return analysis.dict(), "local"


def render_cluster_chart(issues):
    counts = {}
    for issue in issues:
        label = issue["cluster_label"]
        counts[label] = counts.get(label, 0) + 1

    chart_data = [
        {
            "Theme": CLUSTER_THEME_NAMES.get(label, f"Theme {label}"),
            "Count": count,
            "Cluster": f"Theme {label}",
        }
        for label, count in sorted(counts.items())
    ]
    fig = px.bar(
        chart_data,
        x="Theme",
        y="Count",
        color="Theme",
        title="Cluster Distribution",
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_layout(showlegend=False, xaxis_title="Risk Theme", yaxis_title="Issue Count")
    return fig


def build_issue_table(issues):
    return [
        {
            "Issue ID": issue["issue_id"],
            "Description": issue["description"],
            "Cluster": issue["cluster_label"],
            "Theme": CLUSTER_THEME_NAMES.get(issue["cluster_label"], f"Theme {issue['cluster_label']}"),
        }
        for issue in issues
    ]


def render_hygiene_cards(hygiene_results):
    if not hygiene_results:
        st.info("No hygiene results available.")
        return

    for result in hygiene_results:
        with st.expander(f"Issue {result['issue_id']} — Score {result['score']}"):
            st.markdown("**Key issues found:**")
            for issue_text in result["issues"]:
                st.write(f"- {issue_text}")
            st.markdown("**Suggested improvements:**")
            for suggestion in result["suggestions"]:
                st.write(f"- {suggestion}")


def check_backend_status():
    try:
        response = requests.get(HEALTH_URL, timeout=3)
        return response.status_code == 200
    except Exception:
        return False


def run():
    st.set_page_config(page_title="Helios AI Risk Dashboard", layout="wide")

    st.markdown("# Helios AI Non-Financial Risk Intelligence")
    st.markdown(
        "Harness risk intelligence for operational issue reporting with cluster themes, duplicate detection, and issue hygiene scoring."
    )

    sidebar = st.sidebar
    sidebar.header("Dashboard Controls")
    backend_online = check_backend_status()
    sidebar.markdown(
        "This dashboard uses the backend API when available. If the backend is offline, it falls back to local analysis."
    )
    sidebar.markdown(f"**Backend status:** {'Online' if backend_online else 'Offline'}")
    run_analysis = sidebar.button("Run Analysis")

    if run_analysis:
        with st.spinner("Analyzing issues..."):
            analysis_data, source = fetch_analysis()

        st.success(f"Analysis completed using {source} engine")

        issues = analysis_data.get("issues", [])
        duplicates = analysis_data.get("duplicate_pairs", [])
        hygiene_results = analysis_data.get("hygiene_results", [])

        total_issues = len(issues)
        total_clusters = len({issue["cluster_label"] for issue in issues})
        total_duplicates = len(duplicates)
        total_hygiene = len(hygiene_results)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Issues analyzed", total_issues)
        col2.metric("Clusters found", total_clusters)
        col3.metric("Duplicate pairs", total_duplicates)
        col4.metric("Hygiene reviews", total_hygiene)

        st.markdown("---")
        with st.container():
            st.subheader("Theme Distribution")
            st.plotly_chart(render_cluster_chart(issues), use_container_width=True)

        st.markdown("---")
        st.subheader("Issue Summary")
        st.dataframe(build_issue_table(issues), use_container_width=True)

        with st.expander("View duplicate / similar issue pairs", expanded=True):
            if duplicates:
                st.table(
                    [
                        {
                            "Issue A ID": pair["issue_a_id"],
                            "Issue B ID": pair["issue_b_id"],
                            "Similarity": pair["similarity"],
                            "Issue A": pair["issue_a_text"],
                            "Issue B": pair["issue_b_text"],
                        }
                        for pair in duplicates
                    ]
                )
            else:
                st.info("No duplicate issue pairs exceeded the similarity threshold.")

        st.markdown("---")
        st.subheader("Issue Hygiene Review")
        render_hygiene_cards(hygiene_results)

        st.markdown(
            "---\n"
            "**Note:** Run the backend with `uvicorn app.main:app --reload` to use the API endpoint instead of local fallback."
        )


if __name__ == "__main__":
    run()
