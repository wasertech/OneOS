from client.chains.tools import get_all_tools, __retriever__ as R

all_tools = get_all_tools()
retriever = R.get_retriever(k=3)

def get_relevant_tools_from_query(query):
    docs = R.get_relevant_docs_from_retriever(retriever, query)
    return [all_tools[d.metadata["index"]] for d in docs]
