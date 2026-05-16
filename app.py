import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
from groq import Groq
import datetime

st.set_page_config(
    page_title="AI Market Mood Agent",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# -------------------- GLOBAL CSS --------------------
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header[data-testid="stHeader"] {display: none;}
    .stApp { background: #0b0d14; }
    [data-testid="stAppViewContainer"] { background: #0b0d14; }
    .block-container {
        padding: 2rem 1rem 3rem !important;
        max-width: 560px !important;
    }
    /* Button styled to match dark theme */
    .stButton > button {
        width: 100%;
        padding: 14px !important;
        background: rgba(89,144,255,0.08) !important;
        border: 0.5px solid rgba(89,144,255,0.25) !important;
        border-radius: 10px !important;
        color: rgba(89,144,255,0.9) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        letter-spacing: 0.01em !important;
        transition: background 0.15s !important;
        margin-top: 0.25rem !important;
        margin-bottom: 0.25rem !important;
    }
    .stButton > button:hover {
        background: rgba(89,144,255,0.16) !important;
        border-color: rgba(89,144,255,0.4) !important;
        color: rgba(89,144,255,1) !important;
    }
    /* Audio player */
    .stAudio {
        background: #111420 !important;
        border-radius: 10px !important;
        padding: 4px !important;
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# -------------------- SETUP --------------------
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=GROQ_API_KEY)

# -------------------- FUNCTIONS --------------------
def get_market_data():
    btc = yf.Ticker("BTC-USD").history(period="5d")['Close']
    spy = yf.Ticker("SPY").history(period="5d")['Close']
    btc_vol    = round(btc.pct_change().dropna().std() * 100, 2)
    spy_vol    = round(spy.pct_change().dropna().std() * 100, 2)
    btc_change = round((btc.iloc[-1] - btc.iloc[-2]) / btc.iloc[-2] * 100, 2)
    spy_change = round((spy.iloc[-1] - spy.iloc[-2]) / spy.iloc[-2] * 100, 2)
    return btc_vol, spy_vol, btc_change, spy_change

def get_market_mood(btc_vol, spy_vol):
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
        max_tokens=60
    )
    return response.choices[0].message.content.strip()

def get_mood_tags(mood_text):
    tag_keywords = [
        "ambient", "lo-fi", "lofi", "techno", "dark", "calm", "energetic",
        "upbeat", "melancholic", "atmospheric", "tense", "neutral", "peaceful",
        "minor", "major", "slow", "fast", "textural", "cinematic", "electronic",
        "jazz", "classical", "noise", "drone", "pulse"
    ]
    found = [t for t in tag_keywords if t in mood_text.lower()]
    return found[:5] if found else ["neutral", "atmospheric"]

def select_track(mood_text):
    mood_lower = mood_text.lower()
    track_map = {
        "dark":        ("dark_melancholic.mp3",   "Dark Melancholic",    "🌑", "4:12"),
        "melancholic": ("dark_melancholic.mp3",   "Dark Melancholic",    "🌑", "4:12"),
        "tense":       ("dark_melancholic.mp3",   "Dark Melancholic",    "🌑", "4:12"),
        "calm":        ("calm_ambient.mp3",        "Calm Ambient",        "🌊", "3:42"),
        "ambient":     ("calm_ambient.mp3",        "Calm Ambient",        "🌊", "3:42"),
        "peaceful":    ("calm_ambient.mp3",        "Calm Ambient",        "🌊", "3:42"),
        "energetic":   ("energetic_techno.mp3",    "Energetic Techno",    "⚡", "3:58"),
        "upbeat":      ("energetic_techno.mp3",    "Energetic Techno",    "⚡", "3:58"),
        "techno":      ("energetic_techno.mp3",    "Energetic Techno",    "⚡", "3:58"),
        "neutral":     ("neutral_atmospheric.mp3", "Neutral Atmospheric", "🌫️", "4:05"),
        "atmospheric": ("neutral_atmospheric.mp3", "Neutral Atmospheric", "🌫️", "4:05"),
        "uncertain":   ("neutral_atmospheric.mp3", "Neutral Atmospheric", "🌫️", "4:05"),
    }
    for keyword, data in track_map.items():
        if keyword in mood_lower:
            return data
    return ("neutral_atmospheric.mp3", "Neutral Atmospheric", "🌫️", "4:05")

def mood_score(btc_vol, spy_vol):
    combined = (btc_vol + spy_vol * 3) / 4
    score = min(10, max(1, round(combined * 1.8, 1)))
    label = ("Calm" if score < 3.5 else
             "Neutral" if score < 6 else
             "Tense" if score < 8 else "Volatile")
    return score, label

# -------------------- HTML BUILDERS --------------------
SHARED_FONTS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'DM Sans', sans-serif; background: transparent; }
</style>
"""

def build_header(today):
    return SHARED_FONTS + f"""
<style>
.header {{ display:flex; align-items:center; justify-content:space-between; padding:0.25rem 0 1.5rem; }}
.logo-row {{ display:flex; align-items:center; gap:10px; }}
.logo-icon {{
    width:34px; height:34px; background:#161925; border-radius:8px;
    border:0.5px solid rgba(255,255,255,0.1); display:flex; align-items:center;
    justify-content:center; font-size:16px;
}}
.logo-text {{
    font-family:'DM Mono',monospace; font-size:11px; color:rgba(255,255,255,0.3);
    letter-spacing:0.12em; text-transform:uppercase;
}}
.live-badge {{
    display:flex; align-items:center; gap:5px;
    background:rgba(45,156,106,0.08); border:0.5px solid rgba(45,156,106,0.2);
    border-radius:20px; padding:4px 10px; font-size:11px;
    font-family:'DM Mono',monospace; color:#2d9c6a;
}}
.live-dot {{ width:5px; height:5px; border-radius:50%; background:#2d9c6a; animation:pulse 2s ease-in-out infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
.hero-date {{
    font-family:'DM Mono',monospace; font-size:11px; color:rgba(255,255,255,0.2);
    letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.4rem;
}}
.hero-title {{ font-size:1.85rem; font-weight:300; color:#fff; line-height:1.2; letter-spacing:-0.02em; }}
.hero-title strong {{ font-weight:500; color:rgba(255,255,255,0.5); }}
</style>
<div class="header">
  <div class="logo-row">
    <div class="logo-icon">🎵</div>
    <span class="logo-text">Market Mood Agent</span>
  </div>
  <div class="live-badge"><div class="live-dot"></div>Live</div>
</div>
<div class="hero-date">{today}</div>
<div class="hero-title">Today's market<br><strong>sounds like…</strong></div>
"""

def build_metrics_idle():
    return SHARED_FONTS + """
<style>
.metrics-row {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; padding:1rem 0 0.5rem; }}
.metric-card {{ background:#111420; border:0.5px solid rgba(255,255,255,0.07); border-radius:10px; padding:14px 14px 12px; }}
.metric-label {{ font-family:'DM Mono',monospace; font-size:10px; color:rgba(255,255,255,0.25); text-transform:uppercase; letter-spacing:0.09em; margin-bottom:6px; }}
.metric-value {{ font-size:22px; font-weight:400; color:rgba(255,255,255,0.2); }}
.metric-change {{ font-size:11px; margin-top:5px; font-family:'DM Mono',monospace; color:rgba(255,255,255,0.2); }}
</style>
<div class="metrics-row">
  <div class="metric-card">
    <div class="metric-label">BTC vol.</div>
    <div class="metric-value">—</div>
    <div class="metric-change">5d avg</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">SPY vol.</div>
    <div class="metric-value">—</div>
    <div class="metric-change">5d avg</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Mood score</div>
    <div class="metric-value">—</div>
    <div class="metric-change">—</div>
  </div>
</div>
"""

def build_metrics(btc_vol, spy_vol, btc_change, spy_change, score, score_label):
    btc_cls    = "up" if btc_change >= 0 else "down"
    spy_cls    = "up" if spy_change >= 0 else "down"
    btc_arrow  = "↑" if btc_change >= 0 else "↓"
    spy_arrow  = "↑" if spy_change >= 0 else "↓"
    score_color = "#2d9c6a" if score < 4 else ("#c0932b" if score < 7 else "#c0392b")
    return SHARED_FONTS + f"""
<style>
.metrics-row {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:8px; padding:1rem 0 0.5rem; }}
.metric-card {{ background:#111420; border:0.5px solid rgba(255,255,255,0.07); border-radius:10px; padding:14px 14px 12px; }}
.metric-label {{ font-family:'DM Mono',monospace; font-size:10px; color:rgba(255,255,255,0.25); text-transform:uppercase; letter-spacing:0.09em; margin-bottom:6px; }}
.metric-value {{ font-size:22px; font-weight:400; color:#fff; }}
.unit {{ font-size:13px; color:rgba(255,255,255,0.25); margin-left:1px; }}
.metric-change {{ font-size:11px; margin-top:5px; font-family:'DM Mono',monospace; }}
.up {{ color:#2d9c6a; }} .down {{ color:#c0392b; }} .muted {{ color:rgba(255,255,255,0.22); }}
</style>
<div class="metrics-row">
  <div class="metric-card">
    <div class="metric-label">BTC vol.</div>
    <div class="metric-value">{btc_vol}<span class="unit">%</span></div>
    <div class="metric-change {btc_cls}">{btc_arrow} {abs(btc_change)}% today</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">SPY vol.</div>
    <div class="metric-value">{spy_vol}<span class="unit">%</span></div>
    <div class="metric-change {spy_cls}">{spy_arrow} {abs(spy_change)}% today</div>
  </div>
  <div class="metric-card">
    <div class="metric-label">Mood score</div>
    <div class="metric-value" style="color:{score_color}">{score}</div>
    <div class="metric-change muted">{score_label}</div>
  </div>
</div>
"""

def build_mood_and_track(mood, tags, track_name, track_icon, track_dur):
    tag_pills = "".join(f'<span class="tag-pill">{t}</span>' for t in tags)
    wave_bars = "".join(
        f'<div class="wave-bar" style="height:{h}px;animation-delay:{d}s"></div>'
        for h, d in [(18,0),(26,0.1),(14,0.2),(28,0.05),(20,0.15),(24,0.25),
                     (16,0.08),(22,0.18),(12,0.3),(26,0.12),(20,0.22),(18,0.07)]
    )
    return SHARED_FONTS + f"""
<style>
.mood-card {{
    background:#111420; border:0.5px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:1.25rem 1.5rem; margin:1rem 0 0.75rem;
    position:relative; overflow:hidden;
}}
.mood-glow {{
    position:absolute; top:0; right:0; width:200px; height:200px; border-radius:50%;
    background:radial-gradient(circle,rgba(89,144,255,0.05) 0%,transparent 65%);
    transform:translate(40%,-40%); pointer-events:none;
}}
.section-label {{
    font-family:'DM Mono',monospace; font-size:10px; color:rgba(255,255,255,0.2);
    text-transform:uppercase; letter-spacing:0.09em; margin-bottom:10px;
}}
.mood-text {{ font-size:14px; color:rgba(255,255,255,0.7); line-height:1.6; }}
.mood-tags {{ display:flex; gap:6px; flex-wrap:wrap; margin-top:1rem; }}
.tag-pill {{
    background:rgba(255,255,255,0.04); border:0.5px solid rgba(255,255,255,0.1);
    color:rgba(255,255,255,0.35); font-size:11px; font-family:'DM Mono',monospace;
    padding:3px 10px; border-radius:20px;
}}
.track-card {{
    background:#111420; border:0.5px solid rgba(255,255,255,0.07);
    border-radius:12px; padding:1.25rem 1.5rem; margin-bottom:0.75rem;
    display:flex; align-items:flex-start; gap:14px;
}}
.track-cover {{
    width:46px; height:46px; background:#161925; border-radius:8px;
    border:0.5px solid rgba(255,255,255,0.08); display:flex; align-items:center;
    justify-content:center; flex-shrink:0; font-size:20px;
}}
.track-name {{ font-size:14px; font-weight:500; color:rgba(255,255,255,0.85); margin-bottom:3px; }}
.track-meta {{ font-size:11px; font-family:'DM Mono',monospace; color:rgba(255,255,255,0.25); margin-bottom:10px; }}
.waveform {{ display:flex; align-items:center; gap:2px; height:28px; }}
.wave-bar {{ width:2.5px; border-radius:2px; background:rgba(89,144,255,0.4); animation:wave 1.4s ease-in-out infinite; }}
@keyframes wave {{ 0%,100%{{transform:scaleY(0.35)}} 50%{{transform:scaleY(1)}} }}
.now-playing {{
    font-family:'DM Mono',monospace; font-size:10px; color:rgba(255,255,255,0.15);
    text-align:center; letter-spacing:0.08em; text-transform:uppercase; margin-bottom:0.25rem;
}}
</style>
<div class="mood-card">
  <div class="mood-glow"></div>
  <div class="section-label">AI analysis · Groq LLaMA 3</div>
  <div class="mood-text">{mood}</div>
  <div class="mood-tags">{tag_pills}</div>
</div>
<div class="track-card">
  <div class="track-cover">{track_icon}</div>
  <div style="flex:1">
    <div class="track-name">{track_name}</div>
    <div class="track-meta">Auto-selected · {track_dur}</div>
    <div class="waveform">{wave_bars}</div>
  </div>
</div>
<div class="now-playing">▶ audio player below</div>
"""

def build_footer():
    return SHARED_FONTS + """
<style>
.footer {{
    display:flex; justify-content:space-between; align-items:center;
    padding-top:1rem; border-top:0.5px solid rgba(255,255,255,0.05); margin-top:0.5rem;
}}
.footer-text {{ font-family:'DM Mono',monospace; font-size:10px; color:rgba(255,255,255,0.15); letter-spacing:0.04em; }}
.mvp-tag {{
    background:rgba(255,255,255,0.04); border:0.5px solid rgba(255,255,255,0.08);
    color:rgba(255,255,255,0.2); font-size:10px; font-family:'DM Mono',monospace;
    padding:3px 9px; border-radius:20px; letter-spacing:0.06em;
}}
</style>
<div class="footer">
  <span class="footer-text">Yahoo Finance · Groq LLaMA 3.3-70b</span>
  <span class="mvp-tag">MVP v0.1</span>
</div>
"""

# -------------------- MAIN --------------------
today     = datetime.date.today().strftime("%b %d, %Y")
generated = st.session_state.get('generated', False)

# 1. Header + Hero
components.html(build_header(today), height=155, scrolling=False)

# 2. Metrics
if generated:
    components.html(
        build_metrics(
            st.session_state['btc_vol'],
            st.session_state['spy_vol'],
            st.session_state['btc_change'],
            st.session_state['spy_change'],
            st.session_state['score'][0],
            st.session_state['score'][1],
        ),
        height=115, scrolling=False
    )
else:
    components.html(build_metrics_idle(), height=115, scrolling=False)

# 3. Mood + Track (only after generation)
if generated:
    track_file, track_name, track_icon, track_dur = st.session_state['track']
    components.html(
        build_mood_and_track(
            st.session_state['mood'],
            st.session_state['tags'],
            track_name, track_icon, track_dur,
        ),
        height=330, scrolling=False
    )
    st.audio(track_file)

# 4. Button — native Streamlit, outside any iframe
btn_label = "↻  Refresh track" if generated else "▶  Generate today's track"
if st.button(btn_label, use_container_width=True):
    with st.spinner("Fetching market data and querying Groq…"):
        btc_vol, spy_vol, btc_change, spy_change = get_market_data()
        mood  = get_market_mood(btc_vol, spy_vol)
        tags  = get_mood_tags(mood)
        track = select_track(mood)
        score = mood_score(btc_vol, spy_vol)

        st.session_state['btc_vol']    = btc_vol
        st.session_state['spy_vol']    = spy_vol
        st.session_state['btc_change'] = btc_change
        st.session_state['spy_change'] = spy_change
        st.session_state['mood']       = mood
        st.session_state['tags']       = tags
        st.session_state['track']      = track
        st.session_state['score']      = score
        st.session_state['generated']  = True
        st.rerun()

# 5. Footer
components.html(build_footer(), height=55, scrolling=False)
