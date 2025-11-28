from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, invoices

app = FastAPI(title="CleanInvoice Core API", version="0.1.0")

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
app.include_router(invoices.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to CleanInvoice Core API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
