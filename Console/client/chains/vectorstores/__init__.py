import subprocess
import pickle
from pathlib import Path
from langchain.vectorstores import Chroma

from client.chains.data_loaders import SitemapLoader
from client.chains.data_splitter import RecursiveCharacterTextSplitter

def get_vectorstore_from_docs(docs, embeddings, dirpath="db"):
    index_path = Path(f"{dirpath}/index")
    if Path(index_path).exists():
        return Chroma(persist_directory=dirpath, embedding_function=embeddings)
    else:
        return Chroma.from_documents(documents=docs, embedding=embeddings, persist_directory=dirpath)

def download_docs(url):
    print("Downloading docs from {url}".format(url=url))
    command = f"wget -r -A.html '{url}'"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout, stderr

def get_vectorstore_from_readthedocs(readthedocs_url, embeddings, dirpath="docs_db", chunk_size=1000, chunk_overlap=40):
    index_path = Path(f"{dirpath}/index")
    
    if Path(index_path).exists():
        vectorstore = Chroma(persist_directory=dirpath, embedding_function=embeddings)
        return vectorstore
    else:
        protocol, uri = readthedocs_url.split("://")
        # docs_dirpath = Path(uri)
        # if not docs_dirpath.exists():
        #     download_docs(readthedocs_url)
        #     print(f"Documentation has been saved as HTML.")
        # print("Loading docs from {docs_dirpath}".format(docs_dirpath=docs_dirpath))
        loader = SitemapLoader(
            f"{protocol}://{uri.split('/')[0]}/sitemap.xml",
            filter_urls=[readthedocs_url],
        )
        raw_documents = loader.load()
        assert len(raw_documents) > 0, "Documents are empty. Make sure the loader works properly."
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        documents = text_splitter.split_documents(raw_documents)
        vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=dirpath)
            
        return vectorstore