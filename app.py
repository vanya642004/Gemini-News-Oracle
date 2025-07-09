import streamlit as st
from transformers import pipeline
from requests_html import HTMLSession
from datetime import datetime
import csv
import google.generativeai as genai

# Configure Gemini
import os
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('models/gemini-2.0-flash')

# Summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def log_news(category, title, summary):
    with open("news_log.csv", "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), category, title, summary])

@st.cache_data
def get_news():
    session = HTMLSession()
    url = "https://www.livemint.com/"
    req = session.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    articles = req.html.find('li.newsBlock h3 a, h2.imgStory a')
    newslist = []

    for article in articles[:3]:
        try:
            link = next(iter(article.absolute_links), None)
            if not link: continue
            article_req = session.get(link, headers={'User-Agent': 'Mozilla/5.0'})
            title = article_req.html.find('h1.heading', first=True)
            content = article_req.html.find('div.storyPage_storyContent__3xuFc', first=True)

            if title and content:
                summary = summarizer(content.text[:2000], max_length=150, min_length=30, do_sample=False)[0]['summary_text']
                newslist.append({"title": title.text, "summary": summary})
                log_news("Headline", title.text, summary)
        except:
            continue
    return newslist

def gemini_answer(context, question):
    try:
        response = gemini_model.generate_content(f"{context}\n\nQuestion: {question}")
        return response.text
    except:
        return "Gemini could not answer the question."

# Streamlit UI
st.set_page_config(page_title="📰 NewsBot", layout="wide")

st.title("📰 NewsBot - Your AI News Assistant")
news_data = get_news()

if news_data:
    st.subheader("🗞️ Today's Headlines")
    for item in news_data:
        st.markdown(f"**{item['title']}**")
        st.info(item['summary'])

    with st.expander("💬 Ask a question about the news"):
        user_input = st.text_input("Your question")
        if st.button("Ask Gemini"):
            full_context = "\n\n".join([f"{n['title']}\n{n['summary']}" for n in news_data])
            response = gemini_answer(full_context, user_input)
            st.success(response)
else:
    st.warning("No news fetched. Please refresh.")

