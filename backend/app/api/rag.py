"""
API endpoints for RAG (Retrieval-Augmented Generation) operations.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models.database import get_db
from app.services.rag_pipeline import RAGPipeline
from app.utils.text_extractor import TextExtractor

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_knowledge_base(
    agent_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload knowledge base file for RAG.

    - **agent_id**: UUID of the agent
    - **file**: File to upload (TXT, JSON, PDF, DOCX)
    """
    try:
        # Validate file type
        allowed_extensions = ['txt', 'json', 'pdf', 'docx']
        file_ext = file.filename.split('.')[-1].lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_FILE_TYPE",
                        "message": f"File type '{file_ext}' not allowed. Allowed: {', '.join(allowed_extensions)}"
                    }
                }
            )

        # Read file content
        content = await file.read()

        # Extract text
        extractor = TextExtractor()
        text = extractor.extract_from_bytes(content, file_ext)

        # Process with RAG pipeline
        rag_pipeline = RAGPipeline(db)
        chunks_created = await rag_pipeline.process_document(
            text=text,
            agent_id=agent_id,
            metadata={
                "filename": file.filename,
                "file_type": file_ext,
                "file_size": len(content)
            }
        )

        logger.info(f"Knowledge base uploaded: {file.filename} ({chunks_created} chunks)")

        return {
            "document_id": f"doc_{agent_id}_{file.filename}",
            "filename": file.filename,
            "chunks_created": chunks_created,
            "status": "processed"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading knowledge base: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "UPLOAD_FAILED",
                    "message": "Failed to upload knowledge base",
                    "details": str(e)
                }
            }
        )


@router.get("/documents/{agent_id}")
async def list_documents(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    List knowledge base documents for an agent.

    - **agent_id**: UUID of the agent
    """
    try:
        rag_pipeline = RAGPipeline(db)
        has_kb = await rag_pipeline.check_knowledge_base(agent_id)

        return {
            "agent_id": agent_id,
            "has_knowledge_base": has_kb
        }

    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "LIST_FAILED",
                    "message": "Failed to list documents",
                    "details": str(e)
                }
            }
        )


@router.delete("/documents/{agent_id}")
async def delete_knowledge_base(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete entire knowledge base for an agent.

    - **agent_id**: UUID of the agent
    """
    try:
        rag_pipeline = RAGPipeline(db)
        await rag_pipeline.delete_knowledge_base(agent_id)

        logger.info(f"Knowledge base deleted for agent: {agent_id}")

        return {
            "message": "Knowledge base deleted successfully",
            "agent_id": agent_id
        }

    except Exception as e:
        logger.error(f"Error deleting knowledge base: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "DELETE_FAILED",
                    "message": "Failed to delete knowledge base",
                    "details": str(e)
                }
            }
        )
