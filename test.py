from Utils.embedder import generate_embeddings
from Utils.vector_store import search_candidates

query = "I need candidates working in Trichy"

query_embedding = generate_embeddings(query)

results = search_candidates(query_embedding)

print("Matched Users:", results)

