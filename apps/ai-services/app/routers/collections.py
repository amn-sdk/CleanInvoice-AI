from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.collections_agent import CollectionAgent
import os

router = APIRouter(prefix="/collections", tags=["Collections"])

# Initialize agent
try:
    agent = CollectionAgent()
except ValueError:
    agent = None  # Will fail gracefully if no API key

class InvoiceCollectionRequest(BaseModel):
    id: str
    number: str
    amount: float
    customer_name: str
    customer_email: Optional[str] = ""
    days_overdue: int
    payment_history: Optional[str] = "No history"
    strategy: Optional[str] = "STANDARD"

@router.post("/process")
async def process_collection(request: InvoiceCollectionRequest):
    """
    Process an invoice through the collection agent.
    Returns recommended action and generated email.
    """
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Collection agent unavailable. OpenAI API key not configured."
        )
    
    try:
        result = agent.process_invoice(request.model_dump())
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Collection processing failed: {str(e)}"
        )

@router.get("/health")
def collections_health():
    """Check if collections agent is operational."""
    return {
        "status": "ok" if agent else "degraded",
        "service": "Collections Agent",
        "llm_available": agent is not None
    }

@router.post("/test-email")
async def test_email_generation(
    customer_name: str = "Jean Dupont",
    amount: float = 1500.0,
    days_overdue: int = 15
):
    """Test endpoint to generate a collection email."""
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Collection agent unavailable. OpenAI API key not configured."
        )
    
    test_data = {
        "id": "test-001",
        "number": "FA-2024-001",
        "amount": amount,
        "customer_name": customer_name,
        "customer_email": "test@example.com",
        "days_overdue": days_overdue,
        "payment_history": "Good payer, first time late",
        "strategy": "STANDARD"
    }
    
    try:
        result = agent.process_invoice(test_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test failed: {str(e)}"
        )
