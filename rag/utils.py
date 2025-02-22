import os
from qdrant_client import QdrantClient
from langchain.vectorstores.qdrant import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader


def load_pdf(path, collection_name):
    if os.path.isfile(path):
        loader = PyPDFLoader(path)
    elif os.path.isdir(path):
        loader = PyPDFDirectoryLoader(path)
    else:
        raise FileNotFoundError
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=32)
    texts = text_splitter.split_documents(documents)
    embeddings = HuggingFaceEmbeddings(
        model_name=os.environ.get("MODEL_NAME"),
        model_kwargs=dict(device="cpu"),
        encode_kwargs=dict(normalize_embeddings=False),
    )

    return Qdrant.from_documents(
        texts,
        embeddings,
        url=os.environ.get("VDB_URL"),
        collection_name=collection_name,
        prefer_grpc=False,
    )


def get_answers(query: str, collection_name: str, k: int = 5):
    embeddings = HuggingFaceEmbeddings(
        model_name=os.environ.get("MODEL_NAME"),
        model_kwargs=dict(device="cpu"),
        encode_kwargs=dict(normalize_embeddings=False),
    )
    client = QdrantClient(url=os.environ.get("VDB_URL"), prefer_grpc=False)
    db = Qdrant(client=client, embeddings=embeddings, collection_name=collection_name)

    docs = db.similarity_search_with_score(query, k=k)
    return [
        dict(score=score, content=doc.page_content, page=doc.metadata["page"])
        for doc, score in docs
    ]

def delete_collection(collection_name: str):
    client = QdrantClient(url=os.environ.get("VDB_URL"), prefer_grpc=False)
    collections = [collection.name for collection in client.get_collections().collections]
    print(collections)
    if collection_name in collections:
        client.delete_collection(collection_name)
        return True
    return False