# AI Market Mood Agent

Autonomous AI agent that scans market volatility and generates the perfect soundtrack for trading sessions.

## Features
- Real-time BTC & S&P 500 analysis via yfinance
- AI mood detection using Groq GPT-OSS 120B
- Smart music selection (4 curated tracks)
- Zero configuration, 100% free

## Live Demo
👉 https://ai-market-mood-agent-jcpqqwerbeymb25hwjwn99.streamlit.app/

## Tech Stack
- Streamlit (UI)
- Groq (LLM inference)
- yfinance (market data)

## Landing

`landing/` — статический лендинг проекта (moved from the separate Litebotpage repo,
merged 2026-11-08): `index.html` + `wrangler.jsonc` (Cloudflare Pages, project name `litebotpage`).
Deploy: `wrangler deploy` from `landing/` or Cloudflare Pages connected to this repo.
