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

from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException


from core.handlers import (
    ledgerlens_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)

from core.exceptions import LedgerLensException
from core.middleware import LoggingMiddleware
from core.logger import logger

app = FastAPI(title="LedgerLens", version="1.0.0")
app.add_middleware(LoggingMiddleware)

app.add_exception_handler(LedgerLensException, ledgerlens_exception_handler)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.add_exception_handler(HTTPException, http_exception_handler)

app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(router)

logger.info("LedgerLens Application Started")


@app.get("/")
def home():

    return {"message": "LedgerLens Running"}


@app.get("/health")
def health():

    return {"status": "Healthy"}


@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):

    document = Document(filename="sample_invoice.png", status="uploaded")

    db.add(document)
    db.commit()
    db.refresh(document)

    return {"id": document.id, "filename": document.filename, "status": document.status}
