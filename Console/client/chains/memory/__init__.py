from langchain.memory import VectorStoreRetrieverMemory


def get_memory_from_retriever(retriever, memory_key="history"):
    return VectorStoreRetrieverMemory(retriever=retriever, memory_key=memory_key)