"""
Services module
"""
from .model_fetcher import ModelFetcher
from .docling_service import parse_document, parse_documents
from .template_service import (
    upload_template,
    delete_template,
    get_template_by_id,
)
from .vector_service import (
    insert_milvus,
    search_similar_documents,
)

__all__ = [
    "ModelFetcher",
    "parse_document",
    "parse_documents",
    "upload_template",
    "delete_template",
    "get_template_by_id",
    "insert_milvus",
    "search_similar_documents",
]
