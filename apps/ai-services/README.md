# AI Services Setup

## Prerequisites

1. **Tesseract OCR** must be installed on your system
2. **OpenAI API Key** for the collections agent (optional for OCR only)

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

3. Configure environment variables:
```bash
export OPENAI_API_KEY="your-api-key-here"  # Required for collections agent
```

4. Start service:
```bash
./start.sh
# Or manually: uvicorn main:app --reload --port 8001
```

## Test

Service runs on: http://localhost:8001

### Test OCR:
```bash
curl -X POST http://localhost:8001/ocr/extract \
  -F "file=@/path/to/invoice.jpg"
```

### Test Collections Agent:
```bash
curl -X POST "http://localhost:8001/collections/test-email?customer_name=Jean%20Dupont&amount=1500&days_overdue=15"
```

## Features

### OCR Invoice Extraction
- Extracts invoice number, date, amounts, VAT number
- Language Support: French (fra), English (eng)
- Confidence Scoring: Returns extraction confidence (0.0 to 1.0)
- Formats Supported: JPG, PNG (PDF coming soon)

### AI Collection Agent (LangGraph)
- **State Machine**: Manages collection workflow (NOT_DUE → LATE_SOFT → LATE_HARD → NEGOTIATION)
- **LLM Email Generation**: Creates personalized collection emails
- **Adaptive Strategy**: SOFT, STANDARD, AGGRESSIVE tones
- **Escalation Logic**: Automatic escalation for long-overdue invoices
- **Timeline Tracking**: Full audit trail of collection actions
