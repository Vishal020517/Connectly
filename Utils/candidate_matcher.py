from Utils.vector_store import collection

def find_matching_candidates(query_embedding, top_k=5):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return {
        "ids":       results.get("ids", [[]])[0],
        "documents": results.get("documents", [[]])[0],
        "distances": results.get("distances", [[]])[0]
    }