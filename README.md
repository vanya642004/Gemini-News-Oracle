# 🔮 Gemini News Oracle

**Your AI-powered news assistant — summarizing headlines, decoding events, and answering your questions using Google’s Gemini.**

---

## 🚀 Overview

**Gemini News Oracle** is a next-gen AI news application built with **Streamlit**, leveraging:

- Real-time news scraping
- Summarization using **Transformers (BART)**
- Question answering with **Google Gemini 2.0 Flash**
- Clean and intuitive **chat-like UI**

You get curated headlines + deep insights + conversational querying — all in one sleek interface.

---

## 🎯 Features

- 📰 **Live News Fetching**  
  Scrapes top headlines from trusted sources in real-time.

- ✂️ **Summarization with BART**  
  Compresses long news into digestible summaries.

- 🤖 **Gemini-Powered Q&A**  
  Ask contextual questions about the news. Get instant, AI-backed answers.

- 💾 **CSV Logging**  
  Every interaction — logged for traceability and improvement.

---

## 📦 Tech Stack

- `Streamlit`
- `transformers` by Hugging Face
- `google-generativeai`
- `requests-html`
- `torch`
- `CSV for data persistence`

---

## ⚙️ Setup Instructions

### 🔐 1. Gemini API Key

Create a `.streamlit/secrets.toml`:

```toml
GEMINI_API_KEY = "your-gemini-api-key-here"
