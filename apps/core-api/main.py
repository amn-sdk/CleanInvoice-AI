from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, invoices, customers, companies, users, export

app = FastAPI(
    title="CleanInvoice Core API",
    version="0.3.0",
    description="Modern invoice management with AI-powered features and Factur-X compliance"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
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

@app.get("/")
def read_root():
    return {
        "message": "Welcome to CleanInvoice Core API",
        "version": "0.3.0",
        "docs": "/docs",
        "features": ["Authentication", "Invoices", "PDF Export", "Factur-X"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
