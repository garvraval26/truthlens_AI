# 🛡️ TruthLens AI — Fake News Detection & Media Bias Analysis System

An AI-powered, full-stack Streamlit application that detects **fake news**, analyzes
**media bias** (Left / Center / Right), and explains its predictions using
transformer-based NLP models (BERT/RoBERTa).

---

## ✨ Features

- **Beautiful landing page** with animated hero section, feature cards, and live stats
- **News Detector** — paste text or upload `.txt` / `.pdf` / `.docx` files
- **URL Analyzer** — auto-fetch and analyze any news article from a link
- **Media Bias Detection** — Left / Center / Right classification with a visual bias meter
- **Explainable AI** — highlights credibility and sensationalism keyword indicators
- **Dashboard** — key metrics, pie/bar/line charts, recent activity feed
- **History** — search, filter, delete, and export all past analyses (CSV)
- **Analytics** — deeper interactive Plotly charts and summary statistics
- **Settings** — Dark/Light mode, model configuration view, data management
- **Glassmorphic, premium SaaS-style UI** with custom CSS, gradients, and animations

---

## 🗂️ Project Structure

```
fake-news-ai/
├── app.py                  # Main entry point
├── model.py                 # AI model loading & inference
├── database.py               # SQLite database layer
├── utils.py                  # File parsing, URL fetching, validation helpers
├── config.py                  # Central configuration
├── requirements.txt
├── README.md
│
├── assets/
│   └── styles.css            # Custom design system (glassmorphism, gradients, animations)
│
├── pages/
│   ├── dashboard.py
│   ├── detector.py
│   ├── url_analysis.py
│   ├── bias.py
│   ├── analytics.py
│   ├── history.py
│   ├── about.py
│   └── settings.py
│
├── models/                    # Local HuggingFace model cache (auto-created)
├── database/                  # SQLite .db file (auto-created)
├── uploads/                   # Temp upload storage (auto-created)
└── exports/                   # CSV export output (auto-created)
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** PyTorch + Transformers downloads may take a few minutes on first install.
> An internet connection is required the **first time** each model is used, since
> HuggingFace models are downloaded and cached locally in `models/`.

### 2. Run the application

```bash
streamlit run app.py
```

The app will open automatically at **http://localhost:8501**.

---

## 🧠 Models Used

| Purpose | Model | Fallback |
|---|---|---|
| Fake News Classification | `hamzab/roberta-fake-news-classification` | `jy46604790/Fake-News-Bert-Detect` → `distilbert-base-uncased` |
| Media Bias Detection | `facebook/bart-large-mnli` (zero-shot) | Graceful neutral default |

Models are configured in `config.py` and cached via `@st.cache_resource` for fast
repeated inference within a session.

---

## ⚠️ Troubleshooting

| Issue | Solution |
|---|---|
| Model fails to download | Check your internet connection; the app will automatically fall back to a lighter model. |
| PDF text extraction fails | The PDF may be scanned/image-based; try a text-based PDF or paste the content instead. |
| URL fetch fails | Some sites block automated scraping or use heavy JavaScript rendering — try pasting the article text directly. |
| Slow first prediction | The first model call in a session includes model loading time; subsequent calls are much faster. |

---

## 📚 References

- Devlin et al., *BERT: Pre-training of Deep Bidirectional Transformers*, 2018
- Liu et al., *RoBERTa: A Robustly Optimized BERT Pretraining Approach*, 2019
- Wang, W. Y., *LIAR: A Benchmark Dataset for Fake News Detection*, 2017
- [HuggingFace Transformers Docs](https://huggingface.co/docs)
- [Streamlit Docs](https://docs.streamlit.io)

---

## 📄 License

This project was built for educational purposes as a final-year major project.
