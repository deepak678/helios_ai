import logging
from fastapi import APIRouter, HTTPException

from app.models import AnalyzeResponse, DuplicatePair, HygieneResult, IssueOutput
from app.services.clustering import cluster_issues
from app.services.duplication import detect_duplicates
from app.services.embedding import get_embeddings
from app.services.hygiene import evaluate_issue_hygiene
from app.utils.preprocessing import load_issues_from_csv

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze_issues():
    """Analyze issues with embeddings, clustering, duplicate detection, and hygiene scoring."""
    try:
        issues = load_issues_from_csv()
        descriptions = [item["description"] for item in issues]

        embeddings = get_embeddings(descriptions)
        labels = cluster_issues(embeddings, n_clusters=4)
        duplicates = detect_duplicates(issues, embeddings, threshold=0.85)
        hygiene = evaluate_issue_hygiene(issues, max_items=5)

        issue_outputs = [
            IssueOutput(
                issue_id=item["issue_id"],
                description=item["description"],
                cluster_label=int(labels[idx]) if idx < len(labels) else None,
            )
            for idx, item in enumerate(issues)
        ]

        duplicate_outputs = [DuplicatePair(**duplicate) for duplicate in duplicates]
        hygiene_outputs = [HygieneResult(**item) for item in hygiene]

        return AnalyzeResponse(
            issues=issue_outputs,
            duplicate_pairs=duplicate_outputs,
            hygiene_results=hygiene_outputs,
        )
    except Exception as exc:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail=str(exc))
