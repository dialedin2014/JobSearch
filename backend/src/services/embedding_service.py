"""
Embedding service using HuggingFace sentence-transformers.

This module provides text embedding functionality for resume and dream job analysis.
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Service for generating text embeddings using sentence-transformers.
    
    Uses the all-MiniLM-L6-v2 model which produces 384-dimensional embeddings.
    
    Attributes:
        model: SentenceTransformer model instance
        dimension: Embedding vector dimension (384 for all-MiniLM-L6-v2)
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize embedding service.
        
        Args:
            model_name: HuggingFace model identifier
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = 384  # all-MiniLM-L6-v2 dimension

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            numpy array of shape (len(texts), dimension)
        """
        logger.info(f"Encoding {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=False)
        return embeddings

    def encode_single(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text string to embed
            
        Returns:
            numpy array of shape (dimension,)
        """
        return self.encode([text])[0]

    def cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between -1 and 1 (higher is more similar)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        return float(similarity)


# Global embedding service instance
embedding_service = EmbeddingService()
