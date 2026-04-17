# 🚀 PromptGenie — Flask Backend

> AI-Powered Prompt Generator Backend | Python • Flask • ML • Gemini AI

---

## 📌 Overview

This backend powers **PromptGenie**, an Android application that generates optimized AI prompts using a trained machine learning model and Gemini AI.

It combines:

* Machine Learning for prompt scoring
* AI generation for enhancement
* Intelligent fallback systems
* User behavior tracking

---

## ⚙️ Key Features

* 🤖 **ML-based Prompt Scoring**
  Gradient Boosting model trained on **13,000 samples (R² = 0.94)**

* ✨ **Smart Prompt Generation**
  Generates 5 candidates and selects the best automatically

* 🔮 **Gemini AI Integration**
  Enhances low-quality prompts dynamically

* 💡 **Topic Suggestions**
  Generates multiple creative angles per category

* 📊 **Search Tracking System**
  Groups user queries for recommendations

* 💬 **PromptGenie Chatbot**
  Context-aware assistant with fallback intelligence

---

## 🔗 API Endpoints

| Method | Endpoint          | Description               |
| ------ | ----------------- | ------------------------- |
| `POST` | `/generate`       | Generate optimized prompt |
| `POST` | `/suggest-topics` | Get topic suggestions     |
| `POST` | `/track-topic`    | Track user search         |
| `POST` | `/chat`           | Chatbot interaction       |
| `GET`  | `/health`         | Health check              |

---

### ▶️ Example: Generate Prompt

```json
{
  "topic": "machine learning",
  "category": "Coding"
}
```

**Response**

```json
{
  "prompt": "You are a senior ML engineer...",
  "source": "ml_model",
  "success": true
}
```

---

### ▶️ Example: Chat API

```json
{
  "message": "improve this prompt",
  "history": [],
  "context": {
    "topic": "python",
    "category": "Coding",
    "prompt": "..."
  }
}
```

---

## 📂 Project Structure

```
flask-backend/
├── app/
│   ├── routes/          # API routes
│   ├── services/        # Business logic
│   ├── models/          # Data models
├── model/               # ML model & training
├── dataset/             # Data files
├── config.py
├── run.py
├── vercel.json
└── requirements.txt
```

---

## 🛠️ Local Setup

### 1️⃣ Clone repo

```
git clone https://github.com/Anshikamajawdiya/PromptGenie-Backend-.git
cd promptai-backend
```

### 2️⃣ Install dependencies

```
pip install -r requirements.txt
```

### 3️⃣ Create `.env`

```
GEMINI_API_KEY=your_api_key
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### 4️⃣ Run server

```
python run.py
```

Server runs at:

```
http://localhost:5000
```

---

## 🌐 Deployment (Vercel)

1. Import repo on Vercel
2. Select **Other Framework**
3. Deploy
4. Add Environment Variables:

```
GEMINI_API_KEY = your_key
FLASK_ENV      = production
FLASK_DEBUG    = False
```

5. Redeploy project

---

## 📊 ML Model Summary

| Metric     | Value             |
| ---------- | ----------------- |
| Algorithm  | Gradient Boosting |
| Samples    | 13,000            |
| Features   | 20                |
| R² Score   | 0.94              |
| Model Size | 1.07 MB           |

---

## 📦 Tech Stack

* Python (Flask)
* Scikit-learn
* Gemini API
* REST APIs
* Vercel Deployment

---

## ⚠️ Important Notes

* `.env` is not included for security
* API keys must remain private
* Enable CORS for Android integration if needed

---

## 👩‍💻 Author

**Anshika Majawdiya**

---

## 📜 License

MIT License
