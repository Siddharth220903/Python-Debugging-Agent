import logging
logger = logging.getLogger("DebuggingAgent.retriever")

from pathlib import Path

BASE_DIR  = Path(__file__).resolve().parent
import re
import numpy as np

class NoDocumentError(Exception):
    """Raised when documentation retrieval fails to meet the threshold."""
    pass

class RetrievalTool():
    def __init__(self):
        from sentence_transformers import CrossEncoder
        import chromadb
        from chromadb.utils import embedding_functions
        from chromadb.config import Settings

        db_path = str(BASE_DIR / "python_docs_vector_db")
        self.client = chromadb.PersistentClient(
            path=db_path,
        )
        self.emb_fn = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_collection(
            name="python_311_docs", 
            embedding_function=self.emb_fn
        )
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")
        self.confidence_threshold = 1e-1
        logger.info("Initialized Retrieval Tool.")

    def normalize_traceback(self, traceback):
        PATTERNS = [
        # Unix & Windows paths
        (r'([A-Za-z]:\\[^"\s]+|\/[^"\s]+)', '<FILE_PATH>'),

        # Line numbers
        (r'line \d+', 'line <LINE>'),

        # Memory addresses
        (r'0x[0-9a-fA-F]+', '<MEMORY_ADDR>'),

        # UUIDs
        (r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-'
        r'[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
        r'[0-9a-fA-F]{12}', '<UUID>'),

        # Quoted variable names
        (r"name '[_a-zA-Z][_a-zA-Z0-9]*'", "name '<VAR>'"),
    ]
        normalized = traceback
        for pattern, replacement in PATTERNS:
            normalized = re.sub(pattern, replacement, normalized)
        logger.info("Cleaned Terminal Error.")
        return normalized
    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))
    def retrieve(self, terminal_error, top_k=3):
        
        filtered_error = self.normalize_traceback(terminal_error)
        logger.info("Starting content retrieval")
        results = self.collection.query(
            query_texts=[filtered_error], 
            n_results=top_k)
        candidates = results['documents'][0]
        metadatas = results['metadatas'][0]
        if not candidates:
            raise NoDocumentError() 
        
        pairs = [[terminal_error, doc] for doc in candidates]
        raw_scores = self.reranker.predict(pairs)
        scores = self.sigmoid(raw_scores)
        ranked = sorted(zip(scores, candidates, metadatas), key=lambda x: x[0], reverse=True)
        top_score, top_doc, top_meta = ranked[0]
        if top_score > self.confidence_threshold:
            raise NoDocumentError()
        
        print(f"Got a document with score: {top_score}")
        logger.info(f"Got a document with score: {top_score}")
        formatted_output = f"SOURCE: {top_meta['source']}\nCONTENT: {top_doc}"
        return formatted_output


    