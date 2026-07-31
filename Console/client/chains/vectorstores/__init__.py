import subprocess
import pickle
from pathlib import Path
from langchain.vectorstores import Chroma
from langchain.schema import Document

from client.chains.data_loaders import SitemapLoader, UnstructuredURLLoader
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
    

def clean_untruct_doc(doc: Document):
    def recursive_replace(text, old, new):
        while old in text:
            text = text.replace(old, new)
        return text
    
    dc = doc.page_content
    
    dc = recursive_replace(dc, "\n\n", "\n")
    dc = recursive_replace(dc, "\r\n", "\n")
    dc = recursive_replace(dc, "\t\t", "\t")
    dc = recursive_replace(dc, "\n\t\n\t", "\n\t")
    dc = recursive_replace(dc, "\n\t", "\n")
    
    
    
    docs = [
        Document(page_content=d, metadata=doc.metadata) \
        for d in dc.split("\n") \
        if len(d.split(" ")) > 5
    ]
    
    return docs


def get_vectorstore_from_website(url, embeddings, dirpath="docs_db", chunk_size=1000, chunk_overlap=40):
    index_path = Path(f"{dirpath}/index")
    if Path(index_path).exists():
        return Chroma(persist_directory=dirpath, embedding_function=embeddings)
    else:
        protocol, uri = url.split("://")
        # sm_url = f"{protocol}://{uri.split('/')[0]}/sitemap.static.03.xml"
        sm_url = "parlement.ch.sitemap.xml"
        print(f"Scraping {sm_url}")
        # loader = SitemapLoader(
        #    web_path=sm_url,
        #     # filter_urls=[url],
        #     is_local=True,
        #     continue_on_failure=True,
        # )
        url_list = [
            "https://www.parlament.ch/fr/services/news/Pages/2020/20201208121152328194158159038_bsf081.aspx",
            "https://www.parlament.ch/fr/services/news/Pages/2020/20201208122850527194158159038_bsf086.aspx",
            "https://www.parlament.ch/fr/services/news/Pages/2020/20201208123408986194158159038_bsf089.aspx",
        ]
        loader = UnstructuredURLLoader(urls=url_list)
        # loader.requests_kwargs = {"verify": False}
        raw_documents = loader.load()
        rd = []
        for doc in raw_documents:
            rd.extend(clean_untruct_doc(doc))
        print(f"Loaded {len(rd)} documents.")
        assert len(rd) > 0, "Documents are empty. Make sure the loader works properly."
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )
        documents = text_splitter.split_documents(raw_documents)
        vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=dirpath)
        
        return vectorstore
