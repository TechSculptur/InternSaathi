"""
Local sentence embeddings service using sentence-transformers (all-MiniLM-L6-v2).
Caches embeddings on disk for fast startup. Falls back to TF-IDF if model unavailable.
"""
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

import numpy as np

logger = logging.getLogger(__name__)

# Model configuration
MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

# Cache file path
CACHE_DIR = Path(__file__).resolve().parent.parent / "data"
EMBEDDINGS_CACHE_FILE = CACHE_DIR / "embeddings.npy"
EMBEDDINGS_IDS_FILE = CACHE_DIR / "embedding_ids.json"


class EmbeddingService:
    """Service for generating and caching sentence embeddings."""

    def __init__(self):
        self._model = None
        self._model_loaded = False
        self._model_load_failed = False

    def _load_model(self) -> bool:
        """Lazy load the sentence-transformers model."""
        if self._model_loaded or self._model_load_failed:
            return self._model is not None

        try:
            from sentence_transformers import SentenceTransformer
            # This will download the model on first run (~90MB), then use cache
            self._model = SentenceTransformer(MODEL_NAME)
            self._model_loaded = True
            logger.info(f"Loaded sentence-transformers model: {MODEL_NAME}")
            return True
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers model: {e}. Falling back to TF-IDF.")
            self._model_load_failed = True
            self._model = None
            return False

    def encode(self, text: str) -> Optional[np.ndarray]:
        """
        Encode a single text string into an embedding vector.
        Returns None if model unavailable.
        """
        if not self._load_model():
            return None

        try:
            # Normalize the text
            text = text.strip()
            if not text:
                return np.zeros(EMBEDDING_DIM, dtype=np.float32)

            embedding = self._model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            return None

    def encode_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Encode multiple texts into embedding vectors."""
        if not self._load_model():
            return [None] * len(texts)

        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
            return [emb.astype(np.float32) for emb in embeddings]
        except Exception as e:
            logger.error(f"Error encoding batch: {e}")
            return [None] * len(texts)

    def encode_internships(self, internships: List[Any]) -> Dict[str, Optional[np.ndarray]]:
        """
        Encode internships using cached embeddings if available,
        otherwise compute and cache them.
        """
        # Build list of internship IDs and texts
        internship_data = []
        for inst in internships:
            skill_names = " ".join([sk.code.replace("_", " ") for sk in inst.required_skills])
            sec_name = inst.sector.code.replace("_", " ") if inst.sector else ""
            doc = f"{inst.title} {sec_name} {inst.description} {skill_names} {inst.work_mode}"
            internship_data.append((inst.id, doc))

        # Check cache
        cached_embeddings = self._load_cache()
        if cached_embeddings is not None:
            cached_ids, cached_matrix = cached_embeddings
            cached_dict = {cid: cached_matrix[i] for i, cid in enumerate(cached_ids)}

            # Check if all current internships are in cache
            all_cached = all(inst_id in cached_dict for inst_id, _ in internship_data)
            if all_cached:
                logger.info(f"Loaded {len(internship_data)} internship embeddings from cache")
                return {inst_id: cached_dict.get(inst_id) for inst_id, _ in internship_data}

        # Compute missing embeddings
        logger.info("Computing internship embeddings...")
        texts = [doc for _, doc in internship_data]
        embeddings = self.encode_batch(texts)

        # Build result dict
        result = {}
        new_embeddings_list = []
        new_ids_list = []

        for (inst_id, _), emb in zip(internship_data, embeddings):
            result[inst_id] = emb
            if emb is not None:
                new_embeddings_list.append(emb)
                new_ids_list.append(inst_id)

        # Save to cache if we have new embeddings
        if new_embeddings_list:
            self._save_cache(new_ids_list, np.array(new_embeddings_list))

        return result

    def _load_cache(self) -> Optional[tuple]:
        """Load embeddings cache from disk."""
        try:
            if EMBEDDINGS_CACHE_FILE.exists() and EMBEDDINGS_IDS_FILE.exists():
                import json
                with open(EMBEDDINGS_IDS_FILE, "r") as f:
                    ids = json.load(f)
                matrix = np.load(EMBEDDINGS_CACHE_FILE)
                if len(ids) == matrix.shape[0]:
                    logger.info(f"Loaded embeddings cache: {len(ids)} internships")
                    return ids, matrix
        except Exception as e:
            logger.warning(f"Failed to load embeddings cache: {e}")
        return None

    def _save_cache(self, ids: List[str], matrix: np.ndarray):
        """Save embeddings cache to disk."""
        try:
            import json
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            with open(EMBEDDINGS_IDS_FILE, "w") as f:
                json.dump(ids, f)
            np.save(EMBEDDINGS_CACHE_FILE, matrix)
            logger.info(f"Saved embeddings cache: {len(ids)} internships")
        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")


# Global singleton instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """Get the global embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service