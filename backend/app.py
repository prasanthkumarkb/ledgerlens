from fastapi import FastAPI
from sqlalchemy.orm import Session
from fastapi import Depends
from database.database import Base
from database.database import engine

import models.document
from database.database import get_db
from models.document import Document
from api.routes import router
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LedgerLens",
    version="1.0.0"
)

app.include_router(router)

@app.get("/")
def home():

    return {
        "message": "LedgerLens Running"
    }


@app.get("/health")
def health():

    return {
        "status": "Healthy"
    }
    
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):

    document = Document(
        filename="sample_invoice.png",
        status="uploaded"
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status
    }