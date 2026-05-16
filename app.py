import streamlit as st

# --------------------- НАСТРОЙКА СТРАНИЦЫ ---------------------
st.set_page_config(
    page_title="AI Market Mood Agent",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --------------------- ИНЪЕКЦИЯ CSS ---------------------
st.markdown("""
<style>
    .stApp {
        background: radial-gradient(circle at 20% 20%, #1a1a2e, #0f0f1a);
    }
    header[data-testid="stHeader"] {
        background: transparent;
        backdrop-filter: blur(10px);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stButton > button {
        background: linear-gradient(135deg, #6ee7ff, #b084ff);
        color: #0a0f1f;
        border: none;
        border-radius: 50px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(110,231,255,0.3);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(110,231,255,0.5);
    }
    .stAlert {
        border-radius: 12px;
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255,255,255,0.15);
    }
    .stAudio > div {
        border-radius: 12px;
        overflow: hidden;
    }
    .block-container {
        padding-top: 3rem;
        padding-bottom: 2rem;
    }
    /* Общие стили текста (кроме h1, чтобы не ломать градиент) */
    h2, h3, p, div, label {
        color: #e0e8ff !important;
    }
    /* Заголовок h1 с градиентом */
    h1 {
        font-weight: 700;
        font-size: 2.5rem;
        background: linear-gradient(135deg, #6ee7ff, #b084ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        /* убираем возможный color, чтобы не было конфликтов */
        color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --------------------- ИМПОРТЫ И НАСТРОЙКА ---------------------
import yfinance as yf
from groq import Groq
import datetime

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# --------------------- ФУНКЦИИ ---------------------
def get_market_mood():
    btc = yf.Ticker("BTC-USD").history(period="5d")['Close']
    spy = yf.Ticker("SPY").history(period="5d")['Close']
    btc_vol = round(btc.pct_change().dropna().std() * 100, 2)
    spy_vol = round(spy.pct_change().dropna().std() * 100, 2)

    prompt = f"""You are a music AI. Analyze the market volatility:
- BTC volatility: {btc_vol}%
- S&P 500 volatility: {spy_vol}%

Describe in one sentence what music genre and mood best fit the current market.
Use only tags understandable by music generators (e.g., ambient, techno, lo-fi, dark, energetic).
Reply strictly with one phrase, no extra text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=50
    )
    return response.choices[0].message.content.strip()

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
    return "neutral_atmospheric.mp3"

# --------------------- ИНТЕРФЕЙС (АНГЛИЙСКИЙ) ---------------------
st.title("🎵 AI Market Mood Agent")
st.markdown("The agent scans the market, determines the mood, and picks the right music.")

if st.button("Generate Today's Track"):
    with st.spinner("Analyzing market... querying Groq..."):
        mood = get_market_mood()
        st.session_state['mood'] = mood
        st.session_state['track'] = select_track(mood)
        st.session_state['date'] = datetime.date.today().strftime("%Y-%m-%d")

if 'mood' in st.session_state:
    st.success(f"**{st.session_state['date']}** – Market mood: {st.session_state['mood']}")
    st.audio(st.session_state['track'])
