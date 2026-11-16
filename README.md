# 🌍 GeoIntel AI

**AI-powered geopolitical intelligence briefings, built with Claude and real-time web research.**

GeoIntel AI takes a country name and produces a comprehensive, sourced geopolitical briefing — covering politics, economy, military, foreign relations, and current developments — in under 60 seconds.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38+-FF4B4B?logo=streamlit&logoColor=white)
![Claude API](https://img.shields.io/badge/Claude_API-Anthropic-6B4FBB?logo=anthropic&logoColor=white)
![Tavily](https://img.shields.io/badge/Tavily-Web_Search-orange)

---

## How It Works

GeoIntel AI uses a **3-stage agentic research pipeline**:

```
┌─────────────────────────────────────────────────────┐
│                   User enters country                │
└──────────────────────┬──────────────────────────────┘
                       ▼
         ┌──────────────────────────┐
         │   🧠 STAGE 1: PLAN       │
         │   Claude analyses the     │
         │   country and generates   │
         │   12-15 targeted search   │
         │   queries across 6 topic  │
         │   areas                   │
         └────────────┬─────────────┘
                      ▼
         ┌──────────────────────────┐
         │   🔍 STAGE 2: RESEARCH   │
         │   Tavily executes all     │
         │   queries against the     │
         │   live web, returning     │
         │   60-90 source snippets   │
         └────────────┬─────────────┘
                      ▼
         ┌──────────────────────────┐
         │   ✍️ STAGE 3: SYNTHESISE │
         │   Claude cross-references │
         │   all research into a     │
         │   structured briefing     │
         │   with cited sources      │
         └────────────┬─────────────┘
                      ▼
         ┌──────────────────────────┐
         │   📋 Final Briefing       │
         │   9 sections, all sourced │
         └──────────────────────────┘
```

### Briefing Sections

| Section | What It Covers |
|---------|---------------|
| 🏛️ Country Overview | Official name, capital, population, government type, head of state |
| 📜 Historical Background | Key events shaping today's political landscape |
| ⚖️ Political Landscape | Government structure, ruling party, opposition, elections |
| 💰 Economy | GDP, industries, trade, sanctions, economic challenges |
| 🤝 Foreign Relations | Alliances, adversaries, regional role, disputes |
| 🛡️ Military & Security | Armed forces, conflicts, nuclear status, threats |
| 🔮 Key Issues to Watch | Current developments that could shift the geopolitical position |
| 📋 Bottom Line | Executive summary in 2-3 sentences |
| 🔗 Sources | Every URL used, with descriptions |

---

## Tech Stack

| Component | Technology | Role |
|-----------|-----------|------|
| **LLM** | Claude (Anthropic API) | Research planning + briefing synthesis |
| **Web Search** | Tavily API | Real-time web research |
| **Frontend** | Streamlit | Interactive dashboard UI |
| **Language** | Python 3.10+ | Core application |

### Key AI Engineering Concepts Demonstrated

- **Tool Use / Function Calling** — Claude calls a `web_search` tool via the Anthropic API's tool-use feature
- **Agentic Multi-Stage Pipeline** — Plan → Research → Synthesise pattern, not a single monolithic prompt
- **Structured Output Parsing** — Claude generates JSON research plans that drive downstream execution
- **Context Window Management** — Research dossier is assembled and truncated to fit within Claude's context
- **System Prompt Engineering** — Separate specialised prompts for the planner and synthesiser roles

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/geointel-ai.git
cd geointel-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your API keys

- **Anthropic API key** → [console.anthropic.com](https://console.anthropic.com/)
- **Tavily API key** → [app.tavily.com](https://app.tavily.com/) (free tier available)

### 4. Run the app

```bash
python -m streamlit run app.py
```

Enter your API keys in the sidebar, pick a country, and hit **Generate Briefing**.

---

## Project Structure

```
geointel-ai/
├── app.py                  # Main Streamlit app (3-stage agent + UI)
├── geointel.py             # Phase 1: basic CLI agent (learning reference)
├── geointel_v2.py          # Phase 2: CLI agent with tool use loop
├── geointel_phase1.ipynb   # Phase 1: Jupyter notebook walkthrough
├── requirements.txt
├── .env.example
└── README.md
```

### Evolution of the Project

| Phase | File | What I Built | What I Learnt |
|-------|------|-------------|---------------|
| **1** | `geointel.py` / `.ipynb` | Basic Claude API call with Tavily | API basics, tool definitions, function calling |
| **2** | `geointel_v2.py` | Agent loop with `while True` / `stop_reason` | Agentic patterns, tool result handling, iterative reasoning |
| **3** | `app.py` | Multi-stage pipeline + Streamlit dashboard | Plan-Execute-Synthesise architecture, prompt specialisation, UI design |

---

## Author

**Ronak Kaup** — Data Analyst & AI Enthusiast

- 🌐 [ronakkaup.co.uk](https://ronakkaup.co.uk)
- 💼 [LinkedIn](https://linkedin.com/in/ronak-kaup)

---

## License

MIT
