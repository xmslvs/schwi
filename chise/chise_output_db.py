import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_storage"
))

collection = client.get_or_create_collection(
    name ="sairo_past_messages",
    metadata = {
        "description": "Persistent memory of all past conversations.",
        "usecase": "Used in Chise model prompts to raise the consistency of answers."
    }
    )

from sentence_transformers import SentenceTransformer

emb_fn = SentenceTransformer("all-MiniLM-L6-v2")

def add_msg_to_db(msg, collection, emb_fn):
    docs = [msg["response"]]

    if (msg["user"] != "Sairo"):
        input = True
    else:
        input = False

    collection.add(
        documents=docs,
        embeddings=emb_fn.encode(docs).tolist(),
        ids=["current datetime"],
        metadatas=[{"user" : msg["user"]}, {"input": input}]
    )


def query_collection(msg, emb_fn, collection):
    query = msg["response"]
    query_vec = emb_fn.encode([query]).tolist()[0]

    results = collection.query(
        query_embeddings=[query_vec],
        n_results=2
    )
    print(results["documents"])