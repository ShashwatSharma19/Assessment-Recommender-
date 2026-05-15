"""Hybrid retrieval system combining FAISS vector search and BM25 keyword search."""

import numpy as np
from typing import List, Tuple
from app.catalog import Assessment, Catalog

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    raise ImportError("Please install sentence-transformers and faiss-cpu")

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    raise ImportError("Please install rank-bm25")


class HybridRetriever:
    """Combines FAISS vector search with BM25 keyword search."""

    def __init__(self, catalog: Catalog, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """Initialize retriever with catalog and embedding model."""
        self.catalog = catalog
        self.embedding_model = SentenceTransformer(embedding_model)

        # Build FAISS index
        self.faiss_index = self._build_faiss_index()

        # Build BM25 index
        self.bm25_index, self.tokenized_docs = self._build_bm25_index()

        # Store assessment lookup table for FAISS index
        self.assessment_ids = [a.id for a in catalog.assessments]

    def _build_faiss_index(self) -> faiss.IndexFlatL2:
        """Build FAISS index from assessment descriptions."""
        # Create embedding texts combining name + description
        texts = []
        for assessment in self.catalog.assessments:
            # Combine name, description, roles, and domains for richer embeddings
            text = f"{assessment.name} {assessment.description} " \
                   f"{' '.join(assessment.target_roles)} {' '.join(assessment.domains)}"
            texts.append(text)

        # Generate embeddings
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        embeddings = embeddings.astype('float32')

        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        return index

    def _build_bm25_index(self) -> Tuple[BM25Okapi, List[List[str]]]:
        """Build BM25 index from assessment data."""
        tokenized_docs = []

        for assessment in self.catalog.assessments:
            # Tokenize: combine name, description, roles, domains
            text = f"{assessment.name} {assessment.description} " \
                   f"{' '.join(assessment.target_roles)} {' '.join(assessment.domains)}"

            # Simple tokenization: lowercase, split on whitespace
            tokens = text.lower().split()
            tokenized_docs.append(tokens)

        bm25 = BM25Okapi(tokenized_docs)
        return bm25, tokenized_docs

    def search(self, query: str, k: int = 10, weights: Tuple[float, float] = (0.6, 0.4)) -> List[Assessment]:
        """
        Hybrid search combining FAISS and BM25.

        Args:
            query: Search query
            k: Number of results to return
            weights: (faiss_weight, bm25_weight) - should sum to 1.0

        Returns:
            List of top-k assessments sorted by combined score
        """
        faiss_weight, bm25_weight = weights

        # FAISS search
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True).astype('float32')
        distances, indices = self.faiss_index.search(query_embedding, min(k * 2, len(self.catalog.assessments)))

        # Convert distances to scores (lower distance = higher score)
        # Normalize to 0-1 range
        distances_arr = distances[0]
        max_distance = float(distances_arr.max()) if len(distances_arr) > 0 else 1.0
        faiss_scores = {}
        for idx, dist in zip(indices[0], distances[0]):
            if max_distance > 0:
                score = 1.0 - (float(dist) / max_distance)
            else:
                score = 0.0
            faiss_scores[self.assessment_ids[int(idx)]] = score

        # BM25 search
        tokens = query.lower().split()
        bm25_scores_list = self.bm25_index.get_scores(tokens)

        # Normalize BM25 scores to 0-1
        bm25_scores_list = list(bm25_scores_list) if hasattr(bm25_scores_list, '__iter__') else bm25_scores_list
        max_bm25 = max(bm25_scores_list) if bm25_scores_list else 1.0
        bm25_scores = {}
        for idx, score in enumerate(bm25_scores_list):
            if max_bm25 > 0:
                normalized_score = score / max_bm25
            else:
                normalized_score = 0.0
            bm25_scores[self.assessment_ids[idx]] = normalized_score

        # Combine scores
        combined_scores = {}
        for assessment_id in self.assessment_ids:
            faiss_score = faiss_scores.get(assessment_id, 0.0)
            bm25_score = bm25_scores.get(assessment_id, 0.0)
            combined = (faiss_weight * faiss_score) + (bm25_weight * bm25_score)
            combined_scores[assessment_id] = combined

        # Sort by combined score and return top-k
        sorted_ids = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        top_ids = [aid for aid, _ in sorted_ids[:k]]

        # Return assessments in order
        results = []
        for aid in top_ids:
            assessment = self.catalog.get_by_id(aid)
            if assessment:
                results.append(assessment)

        return results

    def search_multiple_queries(self, queries: List[str], k: int = 10) -> List[Assessment]:
        """
        Search for multiple queries and combine results.

        Returns assessments that appear in results for multiple queries, ranked by frequency.
        """
        all_results = {}

        for query in queries:
            results = self.search(query, k=k)
            for assessment in results:
                if assessment.id not in all_results:
                    all_results[assessment.id] = 0
                all_results[assessment.id] += 1

        # Sort by frequency and return
        sorted_results = sorted(all_results.items(), key=lambda x: x[1], reverse=True)
        results = []
        for aid, _ in sorted_results[:k]:
            assessment = self.catalog.get_by_id(aid)
            if assessment:
                results.append(assessment)

        return results

    def filter_and_search(self, query: str, test_types: List[str] = None,
                         roles: List[str] = None, domains: List[str] = None,
                         k: int = 10) -> List[Assessment]:
        """
        Search with filters.

        Args:
            query: Search query
            test_types: Filter to specific test types (K, C, P)
            roles: Filter to specific target roles
            domains: Filter to specific domains
            k: Number of results

        Returns:
            Filtered and ranked assessments
        """
        # Get search results
        results = self.search(query, k=len(self.catalog.assessments))

        # Apply filters
        filtered = results
        if test_types:
            filtered = [a for a in filtered if a.test_type in test_types]
        if roles:
            filtered = [a for a in filtered if any(r in a.target_roles for r in roles)]
        if domains:
            filtered = [a for a in filtered if any(d in a.domains for d in domains)]

        return filtered[:k]
