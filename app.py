import streamlit as st
import requests
from transformers import pipeline
import os
import google.generativeai as genai

# Show full error in Streamlit UI
st.set_option('client.showErrorDetails', True)

# Load API keys from Streamlit Secrets
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Check for keys and stop early if missing
if not GEMINI_API_KEY or not NEWS_API_KEY:
    st.error("❌ API keys missing. Please add `GEMINI_API_KEY` and `NEWS_API_KEY` in Streamlit secrets.")
    st.stop()

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('models/gemini-2.0-flash')

# Summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@st.cache_data
def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    # Debugging output
    st.write("🔍 NewsAPI Status Code:", response.status_code)
    st.write("🔎 Response Preview:", response.text[:500])  # Show part of the response

    news_items = []

    if response.status_code == 200:
        articles = response.json().get("articles", [])
        for article in articles:
            title = article.get("title", "")
            content = article.get("content", "") or article.get("description", "")
            if content:
                try:
                    summary = summarizer(content[:1000], max_length=120, min_length=30, do_sample=False)[0]['summary_text']
                except Exception as e:
                    summary = content[:200] + "..."
                news_items.append({
                    "title": title.strip(),
                    "summary": summary.strip()
                })
    else:
        st.warning(f"❌ News API error: {response.status_code} - {response.reason}")
    
    return news_items

def gemini_answer(context, question):
    try:
        response = gemini_model.generate_content(f"{context}\n\nQuestion: {question}")
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Gemini Error: {e}"

# ──────────────── UI ────────────────────────
st.set_page_config(page_title="🔮 Gemini News Oracle", layout="wide")
st.title("🔮 Gemini News Oracle")
st.markdown("Summarizing India's headlines and answering your questions using AI.")

news_data = fetch_news()

if news_data:
    st.subheader("🗞️ Top Headlines")
    for item in news_data:
        st.markdown(f"**{item['title']}**")
        st.info(item['summary'])

    st.markdown("---")
    st.subheader("💬 Ask Gemini about the news")
    question = st.text_input("Ask your question:")
    if st.button("Ask Gemini") and question.strip():
        with st.spinner("Generating answer..."):
            context = "\n\n".join([f"{n['title']}\n{n['summary']}" for n in news_data])
            answer = gemini_answer(context, question)
            st.success(answer)
else:
    st.warning("⚠️ Could not fetch headlines at the moment. Check API key or try later.")
