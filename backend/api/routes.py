
import os
import uuid
import json
from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import HTTPException
from fastapi import Depends

from sqlalchemy.orm import Session

from database.database import get_db
from models.document import Document
from schemas.invoice import UploadResponse
from services.vision import extract_invoice
from schemas.invoice import DocumentUpdate
from services.watermark import add_watermark
from fastapi.responses import FileResponse
router = APIRouter()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png"
]

@router.get("/ping")
def ping():

    return {
        "message": "LedgerLens API Working"
    }

@router.get("/health")

def health():
    return {
        "status": "OK"
    }
    
@router.post(
    "/ingest",
    response_model=UploadResponse
)
async def ingest_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG and PNG files are allowed."
        )

    unique_name = f"{uuid.uuid4()}{extension}"

    save_path = os.path.join(
        UPLOAD_FOLDER,
        unique_name
    )

    contents = await file.read()

    with open(save_path, "wb") as f:
        f.write(contents)

    document = Document(
        filename=file.filename,
        image_path=save_path,
        status="uploaded"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "success": True,
        "message": "Document uploaded successfully.",
        "document": document
    }


@router.get("/documents")
def list_documents(
    db: Session = Depends(get_db)
):

    return db.query(Document).all()

@router.post("/extract/{document_id}")
def extract_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.get(
        Document,
        document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    result = extract_invoice(
        document.image_path
    )
    
    processed_image = add_watermark(
    document.image_path,
    document.id
    )

    document.processed_image_path = processed_image

    document.vendor = result.get("vendor")

    document.invoice_number = result.get(
        "invoice_number"
    )

    document.invoice_date = result.get(
        "invoice_date"
    )

    document.currency = result.get(
        "currency"
    )

    document.subtotal = result.get(
        "subtotal"
    )

    document.tax = result.get(
        "tax"
    )

    document.total = result.get(
        "total"
    )

    document.overall_confidence = result.get(
        "confidence"
    )

    document.extracted_json = json.dumps(result)

    document.status = "processed"

    db.commit()
    db.refresh(document)

    return {
        "message":"Invoice extracted",
        "data":result
    }

@router.get("/document/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.get(Document, document_id)

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return document

@router.put("/document/{document_id}")
def update_document(
    document_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db)
):

    document = db.get(Document, document_id)

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    document.vendor = payload.vendor
    document.invoice_number = payload.invoice_number
    document.invoice_date = payload.invoice_date
    document.currency = payload.currency
    document.subtotal = payload.subtotal
    document.tax = payload.tax
    document.total = payload.total
    document.overall_confidence = payload.overall_confidence
    document.status = payload.status

    db.commit()

    db.refresh(document)

    return {
        "message": "Updated Successfully",
        "document": document
    }
    
@router.get("/processed/{document_id}")
def get_processed_image(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = db.get(Document, document_id)

    if document is None:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    if not document.processed_image_path:

        raise HTTPException(
            status_code=404,
            detail="Processed image not found"
        )

    return FileResponse(
        document.processed_image_path
    )