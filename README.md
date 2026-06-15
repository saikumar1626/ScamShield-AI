# 🛡️ ScamShield — Multilingual UPI/Payment Scam Detector with Explainable Tactics

> A real-time, explainable scam-detection system for India's most common financial fraud messages — built to understand **code-mixed regional languages** (Hinglish, Tanglish, Tenglish, Banglish, and more), not just English.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg)](https://fastapi.tiangolo.com/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-orange.svg)](https://scikit-learn.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 🎯 The Problem

India processes over 15 billion UPI transactions a month — and alongside that volume comes a flood of payment scams via SMS and WhatsApp: fake KYC alerts, "you've won a prize" messages, fraudulent refund requests, and OTP-phishing attempts.

Most commercial spam/fraud filters are trained primarily on **English-language data from Western contexts**. They miss the specific phrasing patterns used in **code-mixed Indian languages** — messages that switch between English and Hindi, Tamil, Telugu, or Bengali mid-sentence, often in romanized script ("Unga account 30 nimishathula block aagidum...").

**ScamShield** closes that gap. It doesn't just say "this is a scam" — it explains **which manipulation tactic** is being used (urgency, fake authority, false rewards, credential phishing, etc.), in the language the message was written in, and works live over WhatsApp.

---

## ✨ Key Features

- **Binary scam classification** — TF-IDF + Logistic Regression pipeline, trained and evaluated with per-language/script breakdowns
- **Multi-label tactic detection** — identifies *why* a message is dangerous: urgency, authority impersonation, false reward, loss aversion, credential phishing, suspicious links
- **Evidence extraction** — highlights the exact phrase in the message that triggered each tactic flag
- **Multilingual by design** — extensible "language pack" architecture (JSON-based) currently covering English, Hindi/Hinglish, Tamil/Tanglish, Telugu/Tenglish, and Bengali/Banglish, with native-script and romanized variants
- **Rule-based language/script detection** — Unicode-range detection for native scripts + dictionary-based fuzzy matching for romanized text, with graceful fallback for unsupported languages
- **Live WhatsApp integration** — powered by Twilio's WhatsApp Sandbox; forward any suspicious message and get an instant analysis reply
- **Self-aware evaluation** — `metrics_report.md` documents exactly where the model performs well vs. poorly, broken down by language and script, including low-support warnings rather than misleading perfect scores
- **Feedback loop** — every analysis is logged to SQLite with a correction mechanism, designed to support future retraining

---

## 📸 Live Demo

A real scam message sent over WhatsApp, analyzed and explained in real time:

<p align="center">
  <img src="docs/images/whatsapp_demo.png" alt="ScamShield WhatsApp demo showing a scam message flagged with 97% confidence, detected tactics False Reward and Suspicious Link" width="380"/>
</p>

> *Message: "Congratulations! You won ₹15000 cashback. Click https://bit.ly/payupi"*
> **Response:** ⚠️ This message looks like a SCAM (97% confidence). Detected: False Reward, Suspicious Link. Do not click links or share OTP/PIN.

API documentation (auto-generated via FastAPI/OpenAPI):

<p align="center">
  <img src="docs/images/api_docs.png" alt="ScamShield FastAPI Swagger documentation showing /api/analyze, /api/sms-webhook, /api/feedback, /api/stats endpoints" width="600"/>
</p>

---

## 🏗️ Architecture

```
┌──────────────────┐      ┌───────────────────┐      ┌────────────────────────┐
│  WhatsApp / SMS   │─────▶│   FastAPI Backend  │─────▶│   Detection Pipeline    │
│  (Twilio webhook) │◀─────│   (main.py)        │◀─────│  - Script/lang detector │
└──────────────────┘      │                    │      │  - Binary classifier    │
                           │   Web Dashboard    │      │  - Tactic classifier    │
┌──────────────────┐      │   (static/)        │      │  - Evidence extractor   │
│  Browser UI       │◀────▶│                   │      │  - Explanation builder  │
└──────────────────┘      └─────────┬──────────┘      └────────────────────────┘
                                     │
                                     ▼
                           ┌───────────────────┐
                           │  SQLite (feedback) │
                           │  source: web/sms   │
                           └───────────────────┘
```

### Detection Pipeline

1. **Script & Language Detection** (`detector.py`) — Unicode block ranges identify native scripts (Devanagari, Tamil, Telugu, Bengali, etc.); a fuzzy-matched dictionary of common transliterated words identifies romanized regional languages (Hinglish, Tanglish, Tenglish, Banglish). Falls back to `unsupported`/`ambiguous` gracefully.
2. **Binary Classification** (Model A) — TF-IDF (word + character n-grams) + Logistic Regression, calibrated for probability output.
3. **Multi-Label Tactic Classification** (Model B) — One-vs-rest TF-IDF + Logistic Regression per tactic category, with evidence spans extracted via top-weighted n-gram matching.
4. **Explanation Synthesis** — Template-based natural-language explanation combining the detected tactics and evidence.

---

## 🌐 Language Coverage

| Language | Native Script | Romanized | Status |
|---|---|---|---|
| English | — | ✅ | Production-ready |
| Hindi | ✅ Devanagari | ✅ Hinglish | Production-ready |
| Tamil | ✅ Tamil script | ✅ Tanglish | Production-ready |
| Telugu | ✅ Telugu script | ✅ Tenglish | Growing dataset |
| Bengali | ✅ Bengali script | ✅ Banglish | Growing dataset |
| Kannada, Malayalam, Gujarati, Punjabi, Odia | Script detection only | — | Roadmap (see `docs/adding_a_language.md`) |

Adding a new language requires **zero code changes** — just a new JSON language pack. See [`docs/adding_a_language.md`](docs/adding_a_language.md).

---

## 📊 Evaluation

Full per-language, per-script precision/recall/F1 breakdown is generated automatically and saved to [`models/metrics_report.md`](models/metrics_report.md) on every training run.

Key findings:
- Aggregate metrics can be misleading on a small, imbalanced multilingual dataset — the report explicitly flags low-support (language, script) combinations as **"insufficient data"** rather than reporting potentially perfect-but-meaningless scores.
- Performance on **romanized/code-mixed text** is consistently lower than on native scripts or pure English — this mirrors a real, documented gap in commercial NLP systems and is the core motivation for this project.
- The model was evaluated on a held-out set including real-world scam message formats not present in the training templates, to test generalization beyond synthetic patterns.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/scamshield.git
cd scamshield
pip install -r requirements.txt
cp .env.example .env
```

### Generate the dataset and train the models

```bash
python -m src.dataset_generator
python -m src.train
```

This produces `data/scam_dataset.csv`, the trained model artifacts in `models/`, and `models/metrics_report.md`.

### Run the server

```bash
python -m src.main
```

Visit `http://127.0.0.1:8000` for the web dashboard, or `http://127.0.0.1:8000/docs` for the interactive API documentation.

### (Optional) Connect a live WhatsApp number

See [`docs/twilio_setup.md`](docs/twilio_setup.md) for the full Twilio Sandbox + ngrok setup — takes about 10 minutes and is completely free.

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/analyze` | POST | Analyze a message; returns scam probability, language/script, detected tactics with evidence, and a plain-language explanation |
| `/api/sms-webhook` | POST | Twilio webhook for WhatsApp/SMS — auto-replies with an analysis summary |
| `/api/feedback` | POST | Submit a correction for a previously analyzed message |
| `/api/stats` | GET | Aggregate statistics: tactic frequency, language distribution, web vs. messaging traffic |

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Unga account 30 nimishathula block aagidum, ippo click pannunga: bit.ly/xyz"}'
```

---

## 📁 Project Structure

```
scamshield/
├── data/
│   ├── language_packs/        # Per-language scam/legit templates (extensible)
│   └── scam_dataset.csv        # Generated training dataset
├── docs/
│   ├── adding_a_language.md
│   └── twilio_setup.md
├── models/
│   ├── binary_classifier.pkl
│   ├── tactic_classifier.pkl
│   ├── vectorizers.pkl
│   └── metrics_report.md
├── src/
│   ├── detector.py             # Script/language detection
│   ├── dataset_generator.py    # Multilingual dataset generation
│   ├── train.py                # Training + evaluation
│   ├── inference.py            # Prediction + explanation logic
│   ├── database.py             # SQLite logging
│   └── main.py                 # FastAPI app
└── static/                     # Web dashboard (HTML/CSS/JS)
```

---

## 🔭 Limitations & Future Work

- **Dataset size and balance** vary significantly by language — Telugu and Bengali coverage is currently smaller than Hindi/Tamil/English. The metrics report tracks this transparently.
- **Synthetic-to-real generalization**: the dataset is template-generated and supplemented with a small set of real-world examples; a larger real-world corpus would improve robustness against novel scam phrasing.
- **Romanized text normalization** currently uses fuzzy dictionary matching; a learned transliteration model could improve coverage of spelling variants.
- **Planned**: expand to Kannada, Malayalam, Gujarati, Punjabi, and Odia language packs; multilingual explanation output (currently English-only); a lightweight Android client for on-device SMS scanning.

---

## 🧠 Why This Project

This started as an exploration of a real, underexplored gap: most fraud-detection systems are evaluated almost entirely in English, despite the fact that hundreds of millions of users in India communicate — and get scammed — in code-mixed regional languages. ScamShield is an attempt to build a system that is honest about *where it works and where it doesn't*, rather than optimizing for a single headline accuracy number.

---

## 📄 License

MIT
