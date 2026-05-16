import streamlit as st
import yfinance as yf
from groq import Groq
import datetime
import os

# ------------------------------------------------------------
# Настройка ключей (замени на свои!)
# ------------------------------------------------------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]   # <-- вставь настоящий ключ Groq
client = Groq(api_key=GROQ_API_KEY)

# ------------------------------------------------------------
# Функция: анализ рынка и получение настроения
# ------------------------------------------------------------
def get_market_mood():
    btc = yf.Ticker("BTC-USD").history(period="5d")['Close']
    spy = yf.Ticker("SPY").history(period="5d")['Close']
    btc_vol = round(btc.pct_change().dropna().std() * 100, 2)
    spy_vol = round(spy.pct_change().dropna().std() * 100, 2)

    prompt = f"""Ты — музыкальный AI. Проанализируй рыночную волатильность:
- BTC волатильность: {btc_vol}%
- S&P 500 волатильность: {spy_vol}%

Опиши одним предложением, какой музыкальный жанр и настроение лучше всего соответствуют текущему рынку.
Используй только теги, понятные для музыкального генератора (например: ambient, techno, lo-fi, dark, energetic, etc.).
Ответь строго одной фразой, без лишних пояснений."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=50
    )
    return response.choices[0].message.content.strip()

# ------------------------------------------------------------
# Функция: выбор трека по настроению
# ------------------------------------------------------------
def select_track(mood_text):
    mood_lower = mood_text.lower()
    track_map = {
        "dark": "dark_melancholic.mp3",
        "melancholic": "dark_melancholic.mp3",
        "tense": "dark_melancholic.mp3",
        "calm": "calm_ambient.mp3",
        "ambient": "calm_ambient.mp3",
        "peaceful": "calm_ambient.mp3",
        "energetic": "energetic_techno.mp3",
        "upbeat": "energetic_techno.mp3",
        "techno": "energetic_techno.mp3",
        "neutral": "neutral_atmospheric.mp3",
        "atmospheric": "neutral_atmospheric.mp3",
        "uncertain": "neutral_atmospheric.mp3"
    }
    for keyword, filename in track_map.items():
        if keyword in mood_lower:
            return filename
    return "neutral_atmospheric.mp3"  # дефолт

# ------------------------------------------------------------
# Интерфейс
# ------------------------------------------------------------
st.title("🎵 AI Market Mood Agent")
st.markdown("Агент сканирует рынок, определяет настроение и подбирает музыку.")

if st.button("Создать трек дня"):
    with st.spinner("Анализируем рынок... запрашиваем Groq..."):
        mood = get_market_mood()
        st.session_state['mood'] = mood
        st.session_state['track'] = select_track(mood)
        st.session_state['date'] = datetime.date.today().strftime("%Y-%m-%d")

if 'mood' in st.session_state:
    st.success(f"**{st.session_state['date']}** — рынок: {st.session_state['mood']}")
    st.audio(st.session_state['track'])
