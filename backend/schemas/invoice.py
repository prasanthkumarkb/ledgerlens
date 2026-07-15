from pydantic import BaseModel
from datetime import datetime


class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str

    model_config = {
        "from_attributes": True
    }


class UploadResponse(BaseModel):
    success: bool
    message: str
    document: DocumentResponse
    
    
class InvoiceExtraction(BaseModel):

    vendor: str | None = None

    invoice_number: str | None = None

    invoice_date: str | None = None

    currency: str | None = None

    subtotal: float | None = None

    tax: float | None = None

    total: float | None = None

    confidence: float
    
class DocumentUpdate(BaseModel):

    vendor: str | None = None

    invoice_number: str | None = None

    invoice_date: str | None = None

    currency: str | None = None

    subtotal: float | None = None

    tax: float | None = None

    total: float | None = None

    overall_confidence: float | None = None

    status: str | None = None