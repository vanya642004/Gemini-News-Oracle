import streamlit as st
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from transformers import pipeline
import csv
import os
import google.generativeai as genai

# Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel('models/gemini-2.0-flash')

# Summarizer
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def log_news(category, title, summary):
    with open("news_log.csv", "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), category, title, summary])

@st.cache_data
def get_news():
    url = "https://www.livemint.com/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.select('li.newsBlock h3 a, h2.imgStory a')
    newslist = []

    for a in articles[:3]:
        link = a.get('href')
        if not link:
            continue
        if not link.startswith("http"):
            link = "https://www.livemint.com" + link

        try:
            article_res = requests.get(link, headers=headers)
            article_soup = BeautifulSoup(article_res.content, 'html.parser')

            title = article_soup.find('h1', class_='heading') or article_soup.find('h1', class_='story-title')
            content = (article_soup.find('div', class_='storyPage_storyContent__3xuFc') or
                       article_soup.find('div', class_='articleContent') or
                       article_soup.find('div', class_='story-details'))

            if title and content:
                raw_text = content.get_text(strip=True)[:2000]
                summary = summarizer(raw_text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
                newslist.append({
                    "title": title.get_text(strip=True),
                    "summary": summary
                })
                log_news("Headline", title.get_text(strip=True), summary)
        except Exception as e:
            print("Error processing article:", e)
            continue
    return newslist

def gemini_answer(context, question):
    try:
        response = gemini_model.generate_content(f"{context}\n\nQuestion: {question}")
        return response.text
    except Exception as e:
        return f"Error: {e}"

# ─── UI ─────────────────────────────────────────────────────────
st.set_page_config(page_title="🧠 Gemini News Oracle", layout="wide")

st.title("🔮 Gemini News Oracle")
st.markdown("**Summarizing today's headlines and answering your questions using AI.**")

news_data = get_news()

if news_data:
    st.subheader("🗞️ Top Headlines")
    for item in news_data:
        st.markdown(f"**{item['title']}**")
        st.info(item['summary'])

    st.markdown("---")
    st.subheader("💬 Ask Gemini about the News")
    user_q = st.text_input("Your question:")
    if st.button("Ask"):
        with st.spinner("Thinking..."):
            context = "\n\n".join([f"{n['title']}\n{n['summary']}" for n in news_data])
            response = gemini_answer(context, user_q)
            st.success(response)
else:
    st.warning("Could not fetch headlines at the moment. Try again later.")
