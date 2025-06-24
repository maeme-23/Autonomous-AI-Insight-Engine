from typing import List
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
import logging

class VectorRetriever:
    def __init__(self, data_dir: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.data_dir = data_dir
        self.model_name = model_name
        self.vectorstore = None
        self.embeddings = None
        self.initialized = False

    def initialize(self):
        """Initialize the vector store with documents"""
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"Data directory {self.data_dir} not found")
        
        # Load documents
        loader = DirectoryLoader(self.data_dir, glob="**/*.txt", loader_cls=TextLoader)
        documents = loader.load()
        
        if len(documents) < 10:
            logging.warning(f"Only {len(documents)} documents found. At least 10 recommended.")
        
        # Split documents into chunks
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        
        # Add metadata if not present
        for i, text in enumerate(texts):
            if not hasattr(text, 'metadata') or not text.metadata:
                text.metadata = {"title": f"doc_{i}"}
        
        # Create embeddings and vector store
        self.embeddings = HuggingFaceEmbeddings(model_name=self.model_name)
        self.vectorstore = FAISS.from_documents(texts, self.embeddings)
        self.initialized = True
        logging.info(f"Vector store initialized with {len(texts)} document chunks")

    def retrieve(self, query: str, top_k: int = 3) -> List[Document]:
        """Retrieve top_k most relevant documents for the query"""
        if not self.initialized:
            raise RuntimeError("VectorRetriever not initialized")
        
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        docs = self.vectorstore.similarity_search(query, k=top_k)
        logging.info(f"Retrieved {len(docs)} documents for query: {query}")
        return docs

    def cleanup(self):
        """Clean up resources"""
        self.vectorstore = None
        self.embeddings = None
        self.initialized = False
        logging.info("Vector retriever resources cleaned up")