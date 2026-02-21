# 🧠 Multimodal Conversation Intelligence Engine

An AI-powered, policy-grounded conversation intelligence system that converts raw customer support call audio into structured compliance and risk insights.

Designed for compliance-sensitive industries like **banking**, where fraud detection, regulatory risk, and escalation monitoring are critical.

---

# 🚀 What This Project Does

This system:

1. Accepts a call recording (audio file)
2. Transcribes it using Gemini
3. Retrieves relevant compliance policies (RAG)
4. Extracts structured conversation intelligence
5. Computes deterministic risk scoring
6. Returns a fully structured JSON output

The final output includes:

- Language detection
- Conversation summary
- Customer sentiment
- Sentiment timeline
- Primary intent
- Compliance violations
- Agent performance score
- Threat detection
- Call outcome classification
- Explainability reasoning
- Deterministic risk score & risk band

---

## 🏗 System Architecture

```text
Frontend (UI)
        │
        ▼
FastAPI Backend (api.py)
        │
        ▼
Audio Transcription (Gemini)
        │
        ▼
Policy Retrieval Layer (RAG)
        │
        ▼
Structured Intelligence Extraction (Gemini)
        │
        ▼
Deterministic Risk Engine
        │
        ▼
Final Structured JSON Output
```

---

## 📁 Project Structure

```text
.
├── api.py                  # FastAPI orchestration layer
├── analysis_survey.py      # LLM-based intelligence extraction
├── transcript_service.py   # Audio transcription logic
├── rag_service.py          # Policy retrieval (RAG)
├── risk_engine.py          # Deterministic risk scoring
├── policies.txt            # Banking policy document
├── frontend/
│   └── index.html          # Simple web UI
├── files/                  # Sample audio files
├── requirements.txt
├── .env
└── README.md
```
---

# 🔍 Component Breakdown

## 1️⃣ Frontend (`frontend/index.html`)
- Displays available audio files
- Sends selected file to backend
- Displays JSON analysis
- Allows downloading results

---

## 2️⃣ API Layer (`api.py`)
- Exposes:
  - `/files` → list available audio files
  - `/analyze` → run full pipeline
- Orchestrates:
  - Transcription
  - Policy retrieval
  - LLM analysis
  - Risk scoring
- Returns structured JSON

---

## 3️⃣ Transcription Layer (`transcript_service.py`)
Uses Gemini to:
- Convert audio → text
- Handle multilingual conversations
- Identify speakers (Agent / Customer)

---

## 4️⃣ RAG Layer (`rag_service.py`)
- Retrieves relevant sections from `policies.txt`
- Grounds model reasoning in authoritative compliance rules
- Prevents hallucinated violations

---

## 5️⃣ Intelligence Layer (`analysis_survey.py`)
Uses Gemini to extract:

- Language
- Summary
- Customer sentiment
- Sentiment timeline (3–5 segments)
- Primary intent
- Compliance violations (policy-grounded)
- Agent score (1–10)
- Foul language detection
- Threat detection
- Call outcome
- Explainability reasoning

Output is strictly structured JSON.

---

## 6️⃣ Deterministic Risk Engine (`risk_engine.py`)
Applies rule-based scoring logic:

Example scoring:
- Threat detected → +40
- Compliance violation → +30
- Escalation → +10
- Foul language → +20

Then assigns:
- Low risk
- Medium risk
- High risk

This creates a hybrid AI + rule-based system.

---

# 📦 Sample Output

```json
{
  "language": "English",
  "summary": "Customer reports unauthorized transactions and demands refund.",
  "customer_sentiment": "angry",
  "primary_intent": "fraud complaint",
  "compliance_violations": [],
  "agent_score": 8,
  "foul_language_detected": false,
  "threat_detected": true,
  "compliance_risk_level": "medium",
  "call_outcome": "escalated",
  "sentiment_timeline": [
    {
      "segment": "Customer reports issue",
      "customer_sentiment": "distressed"
    },
    {
      "segment": "Customer demands refund",
      "customer_sentiment": "frustrated"
    },
    {
      "segment": "Customer threatens RBI complaint",
      "customer_sentiment": "angry"
    }
  ],
  "explainability": [
    "Threat of RBI complaint detected",
    "Fraud allegation raised",
    "Escalation to fraud team"
  ],
  "risk_analysis": {
    "risk_score": 75,
    "risk_band": "high",
    "risk_reasoning": [
      "Threat detected",
      "Escalation triggered"
    ]
  }
}
