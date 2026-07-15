# LedgerLens

LedgerLens is an AI-powered invoice processing application that automates invoice data extraction, manual review, document management, and reporting.

The application is built using **FastAPI**, **Streamlit**, **SQLite**, and **OpenAI GPT**.

---

# Features

## Invoice Processing

- Upload invoice images (JPG, JPEG, PNG)
- Automatic AI extraction of invoice information
- Automatic processing immediately after upload
- Invoice watermark generation
- Store invoice data in SQLite

---

## AI Extraction

Extracts the following fields:

- Vendor Name
- Invoice Number
- Invoice Date
- Currency
- Subtotal
- Tax
- Total Amount
- Confidence Score

---

## Manual Review

- View extracted invoice
- Edit extracted values
- Update invoice information
- Change processing status

---

## Dashboard

- Total Documents
- Uploaded Documents
- Processed Documents
- Approved Documents
- Today's Uploads
- Average AI Confidence
- Total Invoice Amount
- Status Distribution Chart
- Daily Upload Chart

---

## Document Management

- Search by Vendor
- Search by Filename
- Filter by Status
- Pagination
- Sorting

---

## Logging

- Request Logging
- Upload Logging
- AI Extraction Logging
- Error Logging
- Database Logging

---

## Error Handling

- Global Exception Handling
- Validation Errors
- HTTP Errors
- Database Errors
- AI Extraction Errors

---

# Technology Stack

## Backend

- FastAPI
- SQLAlchemy
- SQLite
- OpenAI API
- Pillow

## Frontend

- Streamlit
- Pandas
- Requests
- Matplotlib

---

# Project Structure

```
ledgerlens/

│

├── backend/

│   ├── api/

│   ├── core/

│   ├── database/

│   ├── models/

│   ├── schemas/

│   ├── services/

│   ├── uploads/

│   ├── processed/

│   ├── logs/

│   ├── app.py

│   └── requirements.txt

│

├── frontend/

│   ├── app.py

│   └── requirements.txt

│

├── README.md

└── .gitignore
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/<your-username>/ledgerlens.git

cd ledgerlens
```

---

## Backend Setup

```bash
cd backend

python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux/Mac

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment

Create a `.env` file inside **backend**

```text
OPENAI_API_KEY=your_openai_api_key

DATABASE_URL=sqlite:///ledgerlens.db

APP_NAME=LedgerLens

DEBUG=True
```

---

## Run Backend

```bash
uvicorn app:app --reload
```

Backend runs on

```
http://127.0.0.1:8000
```

---

## Frontend Setup

Open another terminal

```bash
cd frontend

pip install -r requirements.txt
```

Run

```bash
streamlit run app.py
```

Frontend runs on

```
http://localhost:8501
```

---

# Application Workflow

```
Upload Invoice
       │
       ▼
Save Image
       │
       ▼
Store Document
       │
       ▼
AI Invoice Extraction
       │
       ▼
Generate Watermark
       │
       ▼
Save Results
       │
       ▼
Dashboard
       │
       ▼
Manual Review
```

---

# API Endpoints

## Upload Invoice

```
POST /ingest
```

---

## List Documents

```
GET /documents
```

Supports

- Pagination
- Search
- Filter
- Sorting

---

## Get Document

```
GET /document/{id}
```

---

## Update Document

```
PUT /document/{id}
```

---

## Dashboard

```
GET /dashboard
```

---

## Dashboard Status

```
GET /dashboard/status
```

---

## Daily Uploads

```
GET /dashboard/daily
```

---

## Watermarked Image

```
GET /processed/{id}
```

---

# Screens

- Upload Invoice
- Documents
- Manual Review
- Dashboard

---

# Logging

Application logs are stored in

```
backend/logs/ledgerlens.log
```

---

# Generated Files

Uploaded invoices

```
backend/uploads/
```

Processed invoices

```
backend/processed/
```

These folders are ignored by Git.

---

# Future Enhancements

- OCR Integration (Azure Document Intelligence / AWS Textract)
- PDF Invoice Support
- Authentication & Authorization
- User Management
- Export to Excel/PDF
- Email Notifications
- Docker Support
- PostgreSQL Support
- Background Processing with Celery
- Unit & Integration Tests
- CI/CD Pipeline
- Cloud Deployment (AWS/Azure)

---

# Author

**Prasanth Kumar K B**

Assistant Team Lead | Software Engineer

Built as part of the **IIT Roorkee New Age Software Engineering Program Capstone Project**.

---

# License

This project is developed for educational purposes as part of the IIT Roorkee Capstone Project.
