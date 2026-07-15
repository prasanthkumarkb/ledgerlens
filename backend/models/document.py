from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy.sql import func

from database.database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    filename = Column(
        String(255),
        nullable=False
    )

    status = Column(
        String(50),
        default="uploaded"
    )

    vendor = Column(
        String(255)
    )

    invoice_number = Column(
        String(255)
    )

    invoice_date = Column(
        String(100)
    )

    currency = Column(
        String(20)
    )

    subtotal = Column(
        Float
    )

    tax = Column(
        Float
    )

    total = Column(
        Float
    )

    extracted_json = Column(
        Text
    )

    overall_confidence = Column(
        Float
    )

    image_path = Column(
        String(500)
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )