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
from fastapi import Query
from sqlalchemy import asc, desc
from sqlalchemy import func
from datetime import date
from core.exceptions import InvalidFileException
from core.exceptions import DocumentNotFoundException
from core.exceptions import AIExtractionException
from core.exceptions import DatabaseException

router = APIRouter()

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png"]


@router.get("/ping")
def ping():

    return {"message": "LedgerLens API Working"}


@router.get("/health")
def health():
    return {"status": "OK"}


@router.post("/ingest", response_model=UploadResponse)
async def ingest_document(file: UploadFile = File(...), db: Session = Depends(get_db)):

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise InvalidFileException()

    unique_name = f"{uuid.uuid4()}{extension}"

    save_path = os.path.join(UPLOAD_FOLDER, unique_name)

    contents = await file.read()

    with open(save_path, "wb") as f:
        f.write(contents)

    document = Document(filename=file.filename, image_path=save_path, status="uploaded")
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise DatabaseException()

    return {
        "success": True,
        "message": "Document uploaded successfully.",
        "document": document,
    }


@router.get("/documents")
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    vendor: str | None = None,
    filename: str | None = None,
    status: str | None = None,
    invoice_date: str | None = None,
    sort_by: str = "id",
    order: str = "desc",
    db: Session = Depends(get_db),
):

    query = db.query(Document)

    if vendor:
        query = query.filter(Document.vendor.ilike(f"%{vendor}%"))

    if filename:
        query = query.filter(Document.filename.ilike(f"%{filename}%"))

    if status:
        query = query.filter(Document.status == status)

    if invoice_date:
        query = query.filter(Document.invoice_date == invoice_date)

    sort_column = getattr(Document, sort_by, Document.id)

    if order.lower() == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))

    total = query.count()

    documents = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (total + page_size - 1) // page_size,
        "data": documents,
    }


@router.post("/extract/{document_id}")
def extract_document(document_id: int, db: Session = Depends(get_db)):

    document = db.get(Document, document_id)

    if document is None:
        raise DocumentNotFoundException()

    try:

        result = extract_invoice(document.image_path)

    except Exception:
        raise AIExtractionException()

    processed_image = add_watermark(document.image_path, document.id)

    document.processed_image_path = processed_image

    document.vendor = result.get("vendor")

    document.invoice_number = result.get("invoice_number")

    document.invoice_date = result.get("invoice_date")

    document.currency = result.get("currency")

    document.subtotal = result.get("subtotal")

    document.tax = result.get("tax")

    document.total = result.get("total")

    document.overall_confidence = result.get("confidence")

    document.extracted_json = json.dumps(result)

    document.status = "processed"
    try:
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise DatabaseException()

    return {"message": "Invoice extracted", "data": result}


@router.get("/document/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):

    document = db.get(Document, document_id)

    if document is None:

        raise HTTPException(status_code=404, detail="Document not found")

    return document


@router.put("/document/{document_id}")
def update_document(
    document_id: int, payload: DocumentUpdate, db: Session = Depends(get_db)
):

    document = db.get(Document, document_id)

    if document is None:

        raise HTTPException(status_code=404, detail="Document not found")

    document.vendor = payload.vendor
    document.invoice_number = payload.invoice_number
    document.invoice_date = payload.invoice_date
    document.currency = payload.currency
    document.subtotal = payload.subtotal
    document.tax = payload.tax
    document.total = payload.total
    document.overall_confidence = payload.overall_confidence
    document.status = payload.status
    try:
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise DatabaseException()

    return {"message": "Updated Successfully", "document": document}


@router.get("/processed/{document_id}")
def get_processed_image(document_id: int, db: Session = Depends(get_db)):

    document = db.get(Document, document_id)

    if document is None:

        raise HTTPException(status_code=404, detail="Document not found")

    if not document.processed_image_path:

        raise HTTPException(status_code=404, detail="Processed image not found")

    return FileResponse(document.processed_image_path)


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):

    total_documents = db.query(Document).count()

    uploaded = db.query(Document).filter(Document.status == "uploaded").count()

    processed = db.query(Document).filter(Document.status == "processed").count()

    approved = db.query(Document).filter(Document.status == "approved").count()

    reviewed = db.query(Document).filter(Document.status == "reviewed").count()

    avg_confidence = db.query(func.avg(Document.overall_confidence)).scalar()

    total_amount = db.query(func.sum(Document.total)).scalar()

    today = date.today().isoformat()

    today_uploads = (
        db.query(Document).filter(func.date(Document.created_at) == today).count()
    )

    return {
        "total_documents": total_documents,
        "uploaded": uploaded,
        "processed": processed,
        "reviewed": reviewed,
        "approved": approved,
        "today_uploads": today_uploads,
        "average_confidence": round(avg_confidence or 0, 2),
        "total_invoice_amount": round(total_amount or 0, 2),
    }


@router.get("/dashboard/status")
def dashboard_status(db: Session = Depends(get_db)):

    result = (
        db.query(Document.status, func.count(Document.id))
        .group_by(Document.status)
        .all()
    )

    return [{"status": row[0], "count": row[1]} for row in result]


@router.get("/dashboard/daily")
def dashboard_daily(db: Session = Depends(get_db)):

    result = (
        db.query(func.date(Document.created_at), func.count(Document.id))
        .group_by(func.date(Document.created_at))
        .all()
    )

    return [{"date": str(row[0]), "count": row[1]} for row in result]
