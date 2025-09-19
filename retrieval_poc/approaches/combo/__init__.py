"""
Combo Retrievers

This module contains combination retrievers that fuse multiple retrieval approaches
using LlamaIndex's QueryFusionRetriever with reciprocal rerank fusion.

Available combinations:
- DenseText2SQLRetriever: Combines Dense Retrieval + Text2SQL
- DenseBM25Retriever: Combines Dense Retrieval + BM25
- DenseText2SQLBM25Retriever: Combines Dense Retrieval + Text2SQL + BM25
"""

from .dense_text2sql import DenseText2SQLRetriever
from .dense_bm25 import DenseBM25Retriever
from .dense_text2sql_bm25 import DenseText2SQLBM25Retriever

__all__ = [
    "DenseText2SQLRetriever",
    "DenseBM25Retriever", 
    "DenseText2SQLBM25Retriever"
]
