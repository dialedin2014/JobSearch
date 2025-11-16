"""
Embedding service using HuggingFace sentence-transformers and FAISS.

This module provides text embedding and vector store functionality for resume and dream job analysis.
"""

from sentence_transformers import SentenceTransformer
from typing import List, Optional, Tuple
import numpy as np
import logging
import faiss
import os
import pickle

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

    def create_vector_store_from_resume(
        self,
        resume_text: str,
        user_id: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> str:
        """
        Create a FAISS vector store from resume text.

        The resume is chunked into segments, embedded, and stored in a FAISS index
        for efficient similarity search.

        Args:
            resume_text: Full resume text
            user_id: User ID for storing the index
            chunk_size: Size of text chunks in characters
            overlap: Overlap between chunks in characters

        Returns:
            Path to the saved FAISS index file
        """
        logger.info(f"Creating FAISS vector store for user {user_id}")

        # Chunk the resume text
        chunks = self._chunk_text(resume_text, chunk_size, overlap)
        logger.info(f"Created {len(chunks)} chunks from resume")

        if not chunks:
            raise ValueError("No chunks created from resume text")

        # Generate embeddings for all chunks
        embeddings = self.encode(chunks)

        # Create FAISS index
        index = faiss.IndexFlatL2(self.dimension)
        index.add(embeddings.astype('float32'))

        # Save index and chunks to disk
        index_dir = "vector_stores"
        os.makedirs(index_dir, exist_ok=True)

        index_path = os.path.join(index_dir, f"{user_id}_resume.index")
        chunks_path = os.path.join(index_dir, f"{user_id}_resume_chunks.pkl")

        faiss.write_index(index, index_path)

        with open(chunks_path, 'wb') as f:
            pickle.dump(chunks, f)

        logger.info(f"FAISS index saved to {index_path}")
        return index_path

    def load_vector_store(self, user_id: str) -> Optional[Tuple[faiss.Index, List[str]]]:
        """
        Load a FAISS vector store for a user.

        Args:
            user_id: User ID

        Returns:
            Tuple of (FAISS index, list of text chunks) or None if not found
        """
        index_path = os.path.join("vector_stores", f"{user_id}_resume.index")
        chunks_path = os.path.join(
            "vector_stores", f"{user_id}_resume_chunks.pkl")

        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            logger.warning(f"Vector store not found for user {user_id}")
            return None

        # Load index and chunks
        index = faiss.read_index(index_path)

        with open(chunks_path, 'rb') as f:
            chunks = pickle.load(f)

        logger.info(
            f"Loaded vector store for user {user_id} with {len(chunks)} chunks")
        return index, chunks

    def search_similar_chunks(
        self,
        user_id: str,
        query_text: str,
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        """
        Search for similar chunks in a user's resume vector store.

        Args:
            user_id: User ID
            query_text: Query text to search for
            top_k: Number of top results to return

        Returns:
            List of (chunk_text, distance) tuples, sorted by similarity
        """
        vector_store = self.load_vector_store(user_id)

        if vector_store is None:
            logger.warning(f"No vector store found for user {user_id}")
            return []

        index, chunks = vector_store

        # Encode query
        query_embedding = self.encode_single(
            query_text).astype('float32').reshape(1, -1)

        # Search FAISS index
        distances, indices = index.search(
            query_embedding, min(top_k, len(chunks)))

        # Return results
        results = [
            (chunks[idx], float(dist))
            for dist, idx in zip(distances[0], indices[0])
            if idx < len(chunks)
        ]

        logger.info(f"Found {len(results)} similar chunks for query")
        return results

    def _chunk_text(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters
            overlap: Overlap between chunks in characters

        Returns:
            List of text chunks
        """
        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += (chunk_size - overlap)

            # Prevent infinite loop
            if start >= len(text):
                break

        return chunks


# Global embedding service instance
embedding_service = EmbeddingService()
