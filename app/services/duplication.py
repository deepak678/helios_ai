from sklearn.metrics.pairwise import cosine_similarity


def detect_duplicates(issues, embeddings, threshold=0.85):
    """Return duplicate issue pairs with cosine similarity above a threshold."""
    duplicates = []
    if not embeddings or len(embeddings) < 2:
        return duplicates

    similarity_matrix = cosine_similarity(embeddings)
    n = len(issues)

    for i in range(n):
        for j in range(i + 1, n):
            score = float(similarity_matrix[i][j])
            if score >= threshold:
                duplicates.append(
                    {
                        "issue_a_id": int(issues[i]["issue_id"]),
                        "issue_b_id": int(issues[j]["issue_id"]),
                        "similarity": round(score, 3),
                        "issue_a_text": issues[i]["description"],
                        "issue_b_text": issues[j]["description"],
                    }
                )
    return duplicates
