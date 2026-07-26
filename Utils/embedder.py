from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

embedder=NVIDIAEmbeddings(model="nvidia/nv-embed-v1",api_key=os.getenv("NVIDIA_API_KEY"))

def generate_embeddings(text):
    return embedder.embed_query(text)
