from langchain.embeddings import HuggingFaceEmbeddings, SentenceTransformerEmbeddings

def get_embeddings(model_name = "intfloat/e5-large-v2"):
    return HuggingFaceEmbeddings(model_name=model_name)
