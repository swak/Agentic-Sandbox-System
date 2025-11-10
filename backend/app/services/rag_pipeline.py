"""
RAG pipeline service for document processing and semantic search.
"""

import logging
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from openai import AsyncOpenAI
import uuid

from app.models.agent import KnowledgeVector
from app.config import settings

logger = logging.getLogger(__name__)


class RAGPipeline:
    """RAG pipeline for knowledge base processing and retrieval."""

    def __init__(self, db: AsyncSession):
        """
        Initialize RAG pipeline.

        Args:
            db: Database session
        """
        self.db = db
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding vector for text using OpenAI.

        Args:
            text: Text to embed

        Returns:
            1536-dimensional vector
        """
        try:
            response = await self.openai_client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding error: {str(e)}", exc_info=True)
            raise

    async def process_document(
        self,
        text: str,
        agent_id: str,
        metadata: Dict = None
    ) -> int:
        """
        Process document: chunk text, embed, and store in vector database.

        Args:
            text: Document text
            agent_id: Agent UUID
            metadata: Document metadata (filename, page, etc.)

        Returns:
            Number of chunks created
        """
        try:
            # Chunk text
            chunks = self._chunk_text(text)
            logger.info(f"Created {len(chunks)} chunks for agent {agent_id}")

            # Embed and store each chunk
            for i, chunk in enumerate(chunks):
                embedding = await self.embed_text(chunk)

                vector = KnowledgeVector(
                    agent_id=uuid.UUID(agent_id),
                    chunk_text=chunk,
                    embedding=embedding,
                    metadata={
                        **(metadata or {}),
                        'chunk_index': i,
                        'chunk_count': len(chunks)
                    }
                )
                self.db.add(vector)

            await self.db.commit()
            logger.info(f"Stored {len(chunks)} vectors for agent {agent_id}")

            return len(chunks)

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Document processing error: {str(e)}", exc_info=True)
            raise

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to find sentence boundary
            if end < len(text):
                for sep in ['. ', '! ', '? ', '\n']:
                    boundary = text.rfind(sep, start, end)
                    if boundary != -1:
                        end = boundary + 1
                        break

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

        return chunks

    async def retrieve_context(
        self,
        query: str,
        agent_id: str,
        top_k: int = 3
    ) -> List[Dict]:
        """
        Retrieve relevant documents using semantic search.

        Args:
            query: User query
            agent_id: Agent UUID
            top_k: Number of documents to retrieve

        Returns:
            List of dicts with 'text', 'distance', 'metadata'
        """
        try:
            # Embed query
            query_embedding = await self.embed_text(query)

            # Perform vector similarity search
            # Use cosine distance operator <-> from pgvector
            query = text("""
                SELECT
                    chunk_text,
                    embedding <-> CAST(:embedding AS vector) AS distance,
                    metadata
                FROM knowledge_vectors
                WHERE agent_id = :agent_id
                ORDER BY distance
                LIMIT :top_k
            """)

            result = await self.db.execute(
                query,
                {
                    'embedding': str(query_embedding),
                    'agent_id': agent_id,
                    'top_k': top_k
                }
            )

            docs = []
            for row in result:
                docs.append({
                    'text': row.chunk_text,
                    'distance': float(row.distance),
                    'metadata': row.metadata
                })

            logger.info(f"Retrieved {len(docs)} documents for query")
            return docs

        except Exception as e:
            logger.error(f"Context retrieval error: {str(e)}", exc_info=True)
            raise

    async def check_knowledge_base(self, agent_id: str) -> bool:
        """
        Check if agent has knowledge base.

        Args:
            agent_id: Agent UUID

        Returns:
            True if knowledge base exists
        """
        try:
            from sqlalchemy import func
            query = select(func.count(KnowledgeVector.id)).where(
                KnowledgeVector.agent_id == uuid.UUID(agent_id)
            )
            result = await self.db.execute(query)
            count = result.scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Knowledge base check error: {str(e)}", exc_info=True)
            return False

    async def delete_knowledge_base(self, agent_id: str) -> bool:
        """
        Delete all vectors for an agent.

        Args:
            agent_id: Agent UUID

        Returns:
            True if successful
        """
        try:
            from sqlalchemy import delete
            stmt = delete(KnowledgeVector).where(
                KnowledgeVector.agent_id == uuid.UUID(agent_id)
            )
            await self.db.execute(stmt)
            await self.db.commit()
            logger.info(f"Deleted knowledge base for agent {agent_id}")
            return True
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Knowledge base deletion error: {str(e)}", exc_info=True)
            raise
