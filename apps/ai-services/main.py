from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ocr

app = FastAPI(
    title="CleanInvoice AI Services",
    version="0.1.0",
    description="AI-powered invoice reading and collection agent"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ocr.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to CleanInvoice AI Services",
        "version": "0.1.0",
        "services": ["OCR Invoice Extraction"]
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
