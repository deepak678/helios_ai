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
    required_columns = [
        "issue_id",
        "gb_gf",
        "risk_category",
        "status",
        "description",
        "root_cause",
    ]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"CSV must contain the columns: {', '.join(required_columns)}")

    df = df.dropna(subset=["description"]).reset_index(drop=True)
    issues = []
    for _, row in df.iterrows():
        issues.append(
            {
                "issue_id": int(row["issue_id"]),
                "gb_gf": str(row["gb_gf"]).strip() if not pd.isna(row["gb_gf"]) else "",
                "risk_category": str(row["risk_category"]).strip() if not pd.isna(row["risk_category"]) else "",
                "status": str(row["status"]).strip() if not pd.isna(row["status"]) else "",
                "description": str(row["description"]).strip(),
                "root_cause": str(row["root_cause"]).strip() if not pd.isna(row["root_cause"]) else "",
            }
        )
    return issues
