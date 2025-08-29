# 🎓 AI-Driven Drop-Out Prediction & Counseling System

A comprehensive web-based system that combines rule-based logic and machine learning to identify at-risk students early and provide proactive counseling support.

## 🎯 Problem Statement

Many students disengage before term-end marks reveal failures. Risk indicators like falling attendance, declining test scores, or repeated subject failures appear weeks earlier but remain siloed in different spreadsheets. Public institutes lack budgets for heavy analytics platforms.

This system provides a lightweight, transparent, rule-based + ML-enhanced dashboard to fuse data, flag risks, and notify mentors early.

## ✨ Key Features

- **📊 Intelligent Dashboard**: One-glance risk visualization with color-coded alerts
- **🤖 Hybrid AI**: Rule-based + ML prediction for better accuracy
- **📩 Proactive Alerts**: Automatic email/WhatsApp notifications
- **🧑‍🏫 Mentor Empowerment**: AI flags risks, humans make final decisions
- **💸 Low-cost**: Open-source stack perfect for public institutes
- **⚙️ Configurable**: Admin can adjust thresholds via UI

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI Backend│    │   PostgreSQL DB │
│   (TypeScript)  │◄──►│   (Python)      │◄──►│   + ML Models   │
│   + Tailwind    │    │   + ML Pipeline │    │   + Risk Logs   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Docker (optional)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Database Setup

```bash
# Create database and run migrations
cd backend
alembic upgrade head
```

### ML Model Training

```bash
cd backend
python scripts/train_models.py
```

## 📁 Project Structure

```
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Configuration & security
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   └── ml/             # ML pipeline
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API calls
│   │   └── utils/          # Utility functions
│   └── package.json
├── docker-compose.yml       # Development environment
└── README.md
```

## 🔧 Configuration

The system is highly configurable through the admin panel:

- Attendance thresholds
- Score cutoffs
- Risk level definitions
- Notification schedules
- ML model parameters

## 📊 Risk Assessment

### Rule-Based Logic

- **Green (Safe)**: >75% attendance, >60% average score
- **Yellow (Warning)**: 60-75% attendance, 40-60% average score
- **Red (Critical)**: <60% attendance, <40% average score

### ML Enhancement

- Logistic Regression for dropout probability
- Decision Trees for risk factor analysis
- Feature importance ranking

## 📧 Notifications

- **Weekly Reports**: Risk summary to mentors
- **Critical Alerts**: Immediate notifications for red-level risks
- **Guardian Updates**: Regular progress reports
- **Counseling Reminders**: Session scheduling and follow-ups

## 🧑‍🏫 Counseling Module

- Session tracking with notes and outcomes
- Action plan suggestions
- Progress monitoring
- Intervention effectiveness analysis

## 🚀 Deployment

### Local Development

```bash
docker-compose up -d
```

### Production

```bash
# Build and deploy
docker build -t dropout-prediction-system .
docker run -p 8000:8000 dropout-prediction-system
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For support and questions:

- Create an issue in the repository
- Check the documentation
- Contact the development team

---

**Built with ❤️ for better education outcomes**
