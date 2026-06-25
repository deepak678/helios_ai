from pathlib import Path

import pandas as pd


def load_issues_from_csv(csv_path=None):
    """Load issues from CSV and normalize fields for analysis."""
    if csv_path is None:
        base_dir = Path(__file__).resolve().parents[2]
        csv_path = base_dir / "data" / "sample_issues.csv"
    else:
        csv_path = Path(csv_path)

    df = pd.read_csv(csv_path)
    if "issue_id" not in df.columns or "description" not in df.columns:
        raise ValueError("CSV must contain issue_id and description columns.")

    df = df.dropna(subset=["description"]).reset_index(drop=True)
    issues = [
        {"issue_id": int(row["issue_id"]), "description": str(row["description"]).strip()}
        for _, row in df.iterrows()
    ]
    return issues
