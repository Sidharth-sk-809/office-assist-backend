# 🚀 Onboarding Automation Assistant

An AI-powered platform that streamlines employee onboarding for **new joiners** and **HR managers**, automating hiring procedures from day one.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Node.js 16+](https://img.shields.io/badge/Node.js-16+-green.svg)](https://nodejs.org)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

---

## Overview

**Onboarding Automation Assistant** is a comprehensive solution designed to simplify and accelerate the employee onboarding process. It leverages AI to provide instant answers to policy questions, automate document processing, and track onboarding task completion—reducing manual HR workload while ensuring new hires have a smooth start.

### Who Is This For?

| Role | Benefits |
|------|----------|
| **New Joiners** | Get instant answers to policy questions, track onboarding tasks, and submit required documents easily |
| **HR Managers** | Automate repetitive tasks, monitor onboarding progress, and reduce time-to-productivity for new hires |
| **IT Admins** | Easy deployment with Docker, scalable architecture, and comprehensive API |

---

## Key Features

| Feature | Description |
|---------|-------------|
| 💬 **AI Policy Assistant** | Natural language chatbot powered by RAG (Retrieval-Augmented Generation) to answer company policy questions instantly |
| 📝 **Automated Task Management** | Create, assign, and track onboarding tasks with AI-powered completion grading |
| 📄 **Smart Document Processing** | Upload and analyze resumes for experience classification and document validation |
| 👥 **Session Management** | Secure, persistent sessions for new joiners with progress tracking |
| 📊 **Real-time Dashboard** | Live status monitoring and onboarding progress analytics |
| 🔔 **Notifications** | Automated reminders for pending tasks and deadlines |

---

## Quick Start

Get up and running in under 5 minutes:

```bash
# Clone the repository
git clone https://github.com/your-org/onboarding-assistant.git
cd onboarding-assistant

# Start Backend (Terminal 1)
cd office-assist-backend
source venv/bin/activate
python main.py

# Start Frontend (Terminal 2)
cd office-assist-frontend
npm run dev

# Access the application
open http://localhost:3000
```

---

## Installation

### Prerequisites

- **Python** 3.8 or higher
- **Node.js** 16 or higher
- **Google Cloud Platform** account with:
  - Vertex AI API enabled
  - Firestore database
  - Service account credentials

### Step 1: Backend Setup

```bash
cd office-assist-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (see Configuration section)

# Set GCP credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

### Step 2: Frontend Setup

```bash
cd office-assist-frontend

# Install dependencies
npm install

# Optional: Configure API endpoint
echo "VITE_API_URL=/api" > .env
```

### Step 3: Verify Installation

```bash
# Test backend health
curl http://localhost:8000
# Expected: {"status":"healthy","service":"Onboarding Assistant API"}

# Open frontend
open http://localhost:3000
# Dashboard should display "API: Connected" in green
```

---

## Usage

### For New Joiners

1. **Login** with your employee credentials provided by HR
2. **View Dashboard** to see your onboarding progress and pending tasks
3. **Ask Questions** using the AI Policy Assistant for instant answers about company policies
4. **Complete Tasks** and submit them for automated grading
5. **Upload Documents** like your resume for experience verification

### For HR Managers

1. **Monitor Progress** via the admin dashboard
2. **Create Onboarding Plans** with customizable task checklists
3. **Review Submissions** with AI-assisted grading suggestions
4. **Generate Reports** on onboarding metrics and completion rates

---

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and service status |
| `/chat` | POST | Send questions to the AI policy assistant |
| `/classify` | POST | Upload resume for experience classification |
| `/submit-task` | POST | Submit completed onboarding tasks for grading |

### Example: Ask a Policy Question

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the leave policy for new employees?"}'
```

---

## Configuration

### Backend Environment Variables

Create a `.env` file in `office-assist-backend/`:

```bash
# Google Cloud Platform
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=us-central1
VERTEX_SEARCH_DATA_STORE_ID=your-data-store-id

# Server
PORT=8000
DEBUG=false
```

### Frontend Environment Variables (Optional)

Create a `.env` file in `office-assist-frontend/`:

```bash
VITE_API_URL=/api
```

---

## Project Structure

```
onboarding-assistant/
├── office-assist-backend/      # FastAPI backend with Vertex AI
│   ├── main.py                 # Application entry point
│   ├── requirements.txt        # Python dependencies
│   └── services/               # Business logic modules
├── office-assist-frontend/     # React frontend with Vite
│   ├── src/                    # React components
│   └── package.json            # Node dependencies
├── docs/                       # Additional documentation
│   ├── STARTUP_GUIDE.md        # Detailed setup instructions
│   ├── PROJECT_OVERVIEW.md     # Architecture documentation
│   └── QUICK_REFERENCE.md      # Command reference
└── README.md                   # This file
```

---

## Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Frontend** | React 18, Vite, React Router, Axios, Lucide Icons |
| **Backend** | FastAPI, Python 3.8+, Uvicorn |
| **AI/ML** | Google Cloud Vertex AI, RAG with Discovery Engine |
| **Database** | Google Cloud Firestore |
| **Deployment** | Docker, Google Cloud Run |

---

## Deployment

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individually
docker build -t onboarding-backend ./office-assist-backend
docker build -t onboarding-frontend ./office-assist-frontend
```

### Google Cloud Run

```bash
# Deploy backend
cd office-assist-backend
gcloud run deploy onboarding-backend --source .

# Deploy frontend (after building)
cd office-assist-frontend
npm run build
# Deploy dist/ to Cloud Storage or Cloud Run
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Ensure virtual environment is activated and dependencies installed |
| Frontend can't connect | Verify backend is running on port 8000; check CORS settings |
| AI features not working | Check `GOOGLE_APPLICATION_CREDENTIALS` and GCP API enablement |

For detailed troubleshooting, see [STARTUP_GUIDE.md](./docs/STARTUP_GUIDE.md).

---

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and development process.

---

## Support

Need help? Here's how to get support:

- 📖 **Documentation**: Check the [docs/](./docs/) folder
- 🐛 **Bug Reports**: Open an [issue](https://github.com/your-org/onboarding-assistant/issues)
- 💬 **Questions**: Start a [discussion](https://github.com/your-org/onboarding-assistant/discussions)
- 📧 **Email**: contact@your-org.com

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Google Cloud Vertex AI for powering our AI capabilities
- The FastAPI and React communities for excellent frameworks

---

<p align="center">
  <strong>Onboarding Automation Assistant</strong><br>
  Empowering HR teams. Welcoming new talent. Automating the future of work.
</p>

<p align="center">
  <sub>Built with ❤️ for seamless employee onboarding</sub>
</p>

**Version**: 1.0.0 | **Last Updated**: April 2026
