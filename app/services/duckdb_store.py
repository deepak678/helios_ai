import logging
from pathlib import Path

import duckdb
import pandas as pd

from app.services.embedding import get_embeddings
from app.utils.preprocessing import load_issues_from_csv

logger = logging.getLogger(__name__)
DB_PATH = Path(__file__).resolve().parents[2] / "helios_poc.db"


def get_duckdb_connection(db_path=None, read_only=False):
    """Open a DuckDB connection and ensure vector search extension is loaded."""
    if db_path is None:
        db_path = DB_PATH

    conn = duckdb.connect(database=str(db_path), read_only=read_only)

    try:
        conn.execute("INSTALL vss")
    except Exception as exc:
        logger.debug("DuckDB vss install skipped or already installed: %s", exc)

    try:
        conn.execute("LOAD vss")
    except Exception as exc:
        logger.debug("DuckDB vss load skipped or already loaded: %s", exc)

    return conn


def initialize_duckdb(db_path=None):
    """Initialize a local DuckDB database and create the schema."""
    with get_duckdb_connection(db_path=db_path, read_only=False) as conn:
        create_helios_issues_table(conn)


def create_helios_issues_table(conn):
    """Create the issue table for Helios POC risk issues."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS helios_issues (
            issue_id INTEGER PRIMARY KEY,
            gb_gf VARCHAR,
            risk_category VARCHAR,
            status VARCHAR,
            description VARCHAR,
            root_cause VARCHAR,
            issue_embedding FLOAT[1536]
        )
        """
    )


def build_issue_narrative(issue):
    """Construct a clean narrative text for embedding generation."""
    narrative_parts = []
    if issue.get("gb_gf"):
        narrative_parts.append(f"GB/GF: {issue['gb_gf']}")
    if issue.get("risk_category"):
        narrative_parts.append(f"Risk category: {issue['risk_category']}")
    if issue.get("status"):
        narrative_parts.append(f"Status: {issue['status']}")
    if issue.get("root_cause"):
        narrative_parts.append(f"Root cause: {issue['root_cause']}")
    if issue.get("description"):
        narrative_parts.append(f"Description: {issue['description']}")

    return " | ".join(narrative_parts)


def upsert_issues(issues, db_path=None):
    """Upsert a batch of issues into DuckDB with embeddings."""
    if not issues:
        return

    narratives = [build_issue_narrative(issue) for issue in issues]
    embeddings = get_embeddings(narratives)

    rows = [
        (
            int(issue["issue_id"]),
            issue.get("gb_gf"),
            issue.get("risk_category"),
            issue.get("status"),
            issue.get("description"),
            issue.get("root_cause"),
            embedding,
        )
        for issue, embedding in zip(issues, embeddings)
    ]

    with get_duckdb_connection(db_path=db_path, read_only=False) as conn:
        conn.execute("BEGIN TRANSACTION")
        for row in rows:
            conn.execute("DELETE FROM helios_issues WHERE issue_id = ?", [row[0]])
        conn.executemany(
            "INSERT INTO helios_issues (issue_id, gb_gf, risk_category, status, description, root_cause, issue_embedding) VALUES (?, ?, ?, ?, ?, ?, ?)",
            rows,
        )
        conn.execute("COMMIT")
    logger.info("Upserted %s issues into DuckDB", len(rows))


def ingest_issues_from_csv(csv_path=None):
    """Load issues from CSV and ingest them into DuckDB."""
    initialize_duckdb()
    issues = load_issues_from_csv(csv_path)
    upsert_issues(issues)
    return issues


def find_similar_issues(new_issue_vector, risk_category, limit=5, db_path=None):
    """Find similar open issues filtered by risk category using cosine similarity."""
    if not new_issue_vector:
        return []

    query = """
        SELECT
            issue_id,
            gb_gf,
            risk_category,
            status,
            description,
            root_cause,
            array_cosine_similarity(issue_embedding, ?) AS similarity
        FROM helios_issues
        WHERE status = 'OPEN' AND risk_category = ?
        ORDER BY similarity DESC
        LIMIT ?
    """
    with get_duckdb_connection(db_path=db_path, read_only=True) as conn:
        result = conn.execute(query, [new_issue_vector, risk_category, limit]).fetchall()
    return [
        {
            "issue_id": row[0],
            "gb_gf": row[1],
            "risk_category": row[2],
            "status": row[3],
            "description": row[4],
            "root_cause": row[5],
            "similarity": float(row[6]),
        }
        for row in result
    ]


def get_all_open_embeddings(db_path=None):
    """Return a Pandas DataFrame of all open issue IDs and embeddings."""
    with get_duckdb_connection(db_path=db_path, read_only=True) as conn:
        df = conn.execute(
            "SELECT issue_id, issue_embedding FROM helios_issues WHERE status = 'OPEN'"
        ).df()
    return df
