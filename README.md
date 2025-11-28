# CleanInvoice AI 🚀

> Modern invoice management platform with AI-powered features, e-invoicing (Factur-X), and automated debt collection.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Overview

**CleanInvoice AI** is a next-generation SaaS platform designed for SMEs to:
- Manage customer and supplier invoices
- Generate compliant Factur-X e-invoices (French e-invoicing mandate)
- Extract invoice data using AI (OCR + ML models)
- Automate debt collection with AI agents
- Connect to banking systems for payment reconciliation
- Generate tax reports (TVA, e-reporting)

## 🏗️ Tech Stack

### Frontend
- **Next.js 15** (App Router) - React framework
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **shadcn/ui** - UI components
- **TanStack Query** - Data fetching & caching

### Backend
- **FastAPI** - Python API framework
- **PostgreSQL 15** - Database
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **JWT** - Authentication

### AI Services
- **Transformers** (HuggingFace) - Document intelligence
- **LangGraph** - Agent orchestration
- **OpenAI API** - LLM fallback

### Infrastructure
- **Docker & Docker Compose** - Containerization
- **Turborepo** - Monorepo management
- **GitHub Actions** - CI/CD (planned)

## 📁 Project Structure

```
cleaninvoice/
├── apps/
│   ├── web/              # Next.js frontend
│   ├── core-api/         # FastAPI backend (invoices, auth, compliance)
│   └── ai-services/      # AI services (OCR, collections agent)
├── packages/
│   ├── ui/               # Shared UI components
│   ├── types/            # Shared TypeScript types
│   └── config/           # Shared configs (ESLint, Prettier, etc.)
├── infra/
│   └── docker/           # Docker Compose files
└── DATABASE_SETUP.md     # Database setup instructions
```

## 🚀 Quick Start

### Prerequisites
- **Node.js 18+** & npm
- **Python 3.9+**
- **Docker Desktop** (for PostgreSQL)

### 1. Clone the repository

```bash
git clone https://github.com/amn-sdk/CleanInvoice-AI.git
cd CleanInvoice-AI
```

### 2. Install dependencies

**Root (Turborepo):**
```bash
npm install
```

**Backend:**
```bash
cd apps/core-api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start PostgreSQL

```bash
cd infra/docker
docker-compose up -d
```

### 4. Run database migrations

```bash
cd apps/core-api
./venv/bin/alembic upgrade head
```

### 5. Start the services

**Backend API:**
```bash
cd apps/core-api
./start.sh
# API runs on http://localhost:8000
```

**Frontend:**
```bash
cd apps/web
npm run dev
# Web app runs on http://localhost:3000
```

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Available Endpoints

#### Authentication
- `POST /auth/register` - Register new user & company
- `POST /auth/login` - Login (returns JWT token)

#### Invoices
- `GET /invoices/` - List all invoices
- `POST /invoices/` - Create new invoice
- `GET /invoices/{id}` - Get invoice details

## 🗄️ Database Schema

Key tables:
- **companies** - Multi-tenant isolation
- **users** - User accounts with roles
- **customers** / **suppliers** - Business partners
- **invoices** / **invoice_lines** - Core billing entities
- **transactions** / **payments** - Bank reconciliation
- **collection_cases** / **collection_events** - AI agent timeline

See full schema in `apps/core-api/app/models/`

## 🛠️ Development

### Run tests (planned)
```bash
# Backend
cd apps/core-api
pytest

# Frontend
cd apps/web
npm test
```

### Code formatting
```bash
npm run format
```

### Linting
```bash
npm run lint
```

## 📦 EPICs / Roadmap

- [x] **EPIC 0** - Project setup & monorepo
- [x] **EPIC 1** - Database models & migrations
- [ ] **EPIC 2** - Core API (Auth, CRUD)
- [ ] **EPIC 3** - Frontend UI (Login, Dashboard, Invoices)
- [ ] **EPIC 4** - Factur-X & PDF generation
- [ ] **EPIC 5** - AI Invoice OCR
- [ ] **EPIC 6** - AI Collections Agent
- [ ] **EPIC 7** - Banking integration & e-reporting
- [ ] **EPIC 8** - Security, audit, production deployment

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 👨‍💻 Author

**Amine Saddik**
- GitHub: [@amn-sdk](https://github.com/amn-sdk)
- Email: amine.saddik@edu.esiee.fr

---

Built with ❤️ for modern invoice management
