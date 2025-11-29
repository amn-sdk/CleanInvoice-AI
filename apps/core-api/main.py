from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, invoices, customers, companies, users, export, ai, collections

app = FastAPI(
    title="CleanInvoice Core API",
    version="0.5.0",
    description="Modern invoice management with AI-powered features and Factur-X compliance"
)

import os

# CORS middleware for frontend
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(companies.router)
app.include_router(users.router)
app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(export.router)
app.include_router(ai.router)
app.include_router(collections.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to CleanInvoice Core API",
        "version": "0.5.0",
        "docs": "/docs",
        "features": ["Authentication", "Invoices", "PDF Export", "Factur-X", "AI OCR", "AI Collections"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
