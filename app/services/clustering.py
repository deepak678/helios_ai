from sklearn.cluster import KMeans


def cluster_issues(embeddings, n_clusters=4):
    """Cluster issue embeddings into themes using KMeans."""
    if not embeddings:
        return []

    n_samples = len(embeddings)
    n_clusters = min(n_clusters, n_samples)
    if n_clusters <= 0:
        return [0] * n_samples

    model = KMeans(n_clusters=n_clusters, random_state=42)
    labels = model.fit_predict(embeddings)
    return labels.tolist()
