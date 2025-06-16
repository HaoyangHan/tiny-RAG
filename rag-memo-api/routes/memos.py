from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional
from pydantic import BaseModel

from models.memo import Memo
from models.document import Document
from services.memo_generator import MemoGenerator
from services.llm_factory import llm_factory, LLMModel
from dependencies import get_current_user

router = APIRouter(prefix="/memos", tags=["memos"])

class MemoCreate(BaseModel):
    """Schema for creating a new memo."""
    title: str
    document_ids: List[str]
    sections: Optional[List[str]] = None
    model: Optional[str] = None  # LLM model to use

@router.post("/", response_model=Memo)
async def create_memo(
    memo_data: MemoCreate,
    current_user: str = Depends(get_current_user)
) -> Memo:
    """Create a new memo from selected documents."""
    try:
        # Verify all documents exist and belong to user
        documents = []
        for doc_id in memo_data.document_ids:
            document = await Document.get(doc_id)
            if not document:
                raise HTTPException(
                    status_code=404,
                    detail=f"Document {doc_id} not found"
                )
            if document.user_id != current_user:
                raise HTTPException(
                    status_code=403,
                    detail=f"Not authorized to use document {doc_id}"
                )
            documents.append(document)

        # Create memo generator
        memo_generator = MemoGenerator()

        # Generate memo
        memo = await memo_generator.generate_memo(
            title=memo_data.title,
            documents=documents,
            user_id=current_user,
            sections=memo_data.sections,
            model=memo_data.model
        )
        return memo

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating memo: {str(e)}"
        )

@router.get("/models")
async def get_available_models():
    """Get list of available LLM models."""
    try:
        models = llm_factory.get_available_models()
        default_model = llm_factory.get_default_model()
        
        return {
            "models": models,
            "default_model": default_model,
            "model_info": {
                "openai": {
                    LLMModel.GPT_4_MINI: "GPT-4 Mini - Fast and cost-effective",
                    LLMModel.GPT_4_NANO: "GPT-4.1 Nano - Ultra-fast responses"
                },
                "gemini": {
                    LLMModel.GEMINI_2_0_FLASH_LITE: "Gemini 2.0 Flash Lite - Default, balanced performance",
                    LLMModel.GEMINI_2_5_PRO_PREVIEW: "Gemini 2.5 Pro Preview - Advanced reasoning",
                    LLMModel.GEMINI_2_5_FLASH_PREVIEW: "Gemini 2.5 Flash Preview - Fast with thinking"
                }
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving models: {str(e)}"
        )

@router.get("/", response_model=List[Memo])
async def list_memos(
    current_user: str = Depends(get_current_user)
) -> List[Memo]:
    """List all memos for the current user."""
    try:
        memos = await Memo.find(
            Memo.user_id == current_user
        ).to_list()
        return memos

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing memos: {str(e)}"
        )

@router.get("/{memo_id}", response_model=Memo)
async def get_memo(
    memo_id: str,
    current_user: str = Depends(get_current_user)
) -> Memo:
    """Get a specific memo by ID."""
    try:
        memo = await Memo.get(memo_id)
        if not memo:
            raise HTTPException(
                status_code=404,
                detail="Memo not found"
            )
        if memo.user_id != current_user:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to access this memo"
            )
        return memo

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving memo: {str(e)}"
        )

@router.delete("/{memo_id}")
async def delete_memo(
    memo_id: str,
    current_user: str = Depends(get_current_user)
):
    """Delete a memo."""
    try:
        memo = await Memo.get(memo_id)
        if not memo:
            raise HTTPException(
                status_code=404,
                detail="Memo not found"
            )
        if memo.user_id != current_user:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to delete this memo"
            )
        await memo.delete()
        return {"message": "Memo deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting memo: {str(e)}"
        ) 