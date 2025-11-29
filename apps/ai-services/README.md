# AI Services Setup

## Prerequisites

**Tesseract OCR** must be installed on your system:

### macOS:
```bash
brew install tesseract tesseract-lang
```

### Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-fra
```

### Windows:
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

## Setup

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start service:
```bash
./start.sh
# Or manually: uvicorn main:app --reload --port 8001
```

## Test

Service runs on: http://localhost:8001

Test OCR:
```bash
curl -X POST http://localhost:8001/ocr/extract \
  -F "file=@/path/to/invoice.jpg"
```

## Features

- **OCR Invoice Extraction**: Extracts invoice number, date, amounts, VAT number
- **Language Support**: French (fra), English (eng)
- **Confidence Scoring**: Returns extraction confidence (0.0 to 1.0)
- **Formats Supported**: JPG, PNG (PDF coming soon)
