from typing import List, Optional

from pydantic import BaseModel


class IssueOutput(BaseModel):
    issue_id: int
    description: str
    cluster_label: Optional[int]


class DuplicatePair(BaseModel):
    issue_a_id: int
    issue_b_id: int
    similarity: float
    issue_a_text: str
    issue_b_text: str


class HygieneResult(BaseModel):
    issue_id: int
    score: float
    issues: List[str]
    suggestions: List[str]


class AnalyzeResponse(BaseModel):
    issues: List[IssueOutput]
    duplicate_pairs: List[DuplicatePair]
    hygiene_results: List[HygieneResult]
