import streamlit as st
import requests
from transformers import pipeline
import os
import google.generativeai as genai

# Enable error display in UI
st.set_option('client.showErrorDetails', True)

# Configure APIs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('models/gemini-2.0-flash')

# Summarizer pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@st.cache_data
def fetch_news():
    url = f"https://newsapi.org/v2/top-headlines?country=in&language=en&pageSize=5&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    
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
                news_items.append({"title": title, "summary": summary})
    else:
        st.warning(f"Failed to fetch news: {response.status_code}")
    
    return news_items

def gemini_answer(context, question):
    try:
        response = gemini_model.generate_content(f"{context}\n\nQuestion: {question}")
        return response.text.strip()
    except Exception as e:
        return f"Gemini Error: {e}"

# ──────────────────────────────────────────────
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
    question = st.text_input("Your question:")
    if st.button("Ask Gemini") and question.strip():
        with st.spinner("Thinking..."):
            context = "\n\n".join([f"{n['title']}\n{n['summary']}" for n in news_data])
            answer = gemini_answer(context, question)
            st.success(answer)
else:
    st.warning("Could not fetch headlines at the moment. Try again later.")
