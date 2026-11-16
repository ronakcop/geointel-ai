"""
GeoIntel AI — Streamlit App (Globe Dashboard)
===============================================
Inspired by dark globe dashboards with orange accents.
Run with: python -m streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import anthropic
from tavily import TavilyClient
import os
import time
import json

# ─── Page Config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="GeoIntel AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Custom CSS — Dark Globe Theme ───────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Global Reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Dark Background ── */
    .stApp {
        background: #0a0a0f;
        color: #e0e0e0;
    }

    section[data-testid="stSidebar"] {
        background: #0d0d14;
        border-right: 1px solid #1a1a24;
    }

    section[data-testid="stSidebar"] * {
        color: #c0c0c0 !important;
    }

    /* ── Hero Section ── */
    .geo-hero {
        text-align: center;
        padding: 1rem 0 0.5rem 0;
        position: relative;
    }

    .geo-brand {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 0.5rem;
    }

    .geo-brand-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #22c55e;
        display: inline-block;
        box-shadow: 0 0 8px rgba(34, 197, 94, 0.5);
    }

    .geo-brand-text {
        font-size: 0.75rem;
        color: #888;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ── Globe Container ── */
    .globe-section {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 2rem;
        padding: 1rem 0 1.5rem 0;
        position: relative;
    }

    .globe-container {
        width: 320px;
        height: 320px;
        border-radius: 50%;
        background:
            radial-gradient(circle at 35% 35%, rgba(255,107,44,0.15), transparent 60%),
            radial-gradient(circle at 65% 65%, rgba(255,107,44,0.05), transparent 50%),
            radial-gradient(circle at 50% 50%, #12121a 0%, #0a0a0f 100%);
        border: 1px solid rgba(255,107,44,0.15);
        position: relative;
        flex-shrink: 0;
        box-shadow:
            0 0 60px rgba(255,107,44,0.08),
            0 0 120px rgba(255,107,44,0.04),
            inset 0 0 60px rgba(0,0,0,0.5);
    }

    .globe-grid {
        position: absolute;
        inset: 0;
        border-radius: 50%;
        overflow: hidden;
    }

    .globe-grid::before {
        content: '';
        position: absolute;
        width: 100%;
        height: 100%;
        background:
            repeating-linear-gradient(0deg, transparent, transparent 39px, rgba(255,107,44,0.06) 39px, rgba(255,107,44,0.06) 40px),
            repeating-linear-gradient(90deg, transparent, transparent 39px, rgba(255,107,44,0.06) 39px, rgba(255,107,44,0.06) 40px);
        border-radius: 50%;
    }

    .globe-meridian {
        position: absolute;
        border: 1px solid rgba(255,107,44,0.06);
        border-radius: 50%;
        top: 0;
    }
    .globe-meridian-1 { width: 70%; height: 100%; left: 15%; }
    .globe-meridian-2 { width: 40%; height: 100%; left: 30%; }
    .globe-meridian-3 { width: 100%; height: 60%; left: 0; top: 20%; }

    .globe-pin {
        position: absolute;
        width: 14px;
        height: 14px;
        background: #FF6B2C;
        border-radius: 50%;
        border: 2px solid #fff;
        box-shadow: 0 0 16px rgba(255,107,44,0.6), 0 0 40px rgba(255,107,44,0.3);
        z-index: 2;
    }

    .globe-pin-1 { top: 35%; left: 60%; }
    .globe-pin-2 { top: 55%; left: 25%; }
    .globe-pin-3 { top: 25%; left: 45%; }

    .globe-pulse {
        position: absolute;
        width: 30px;
        height: 30px;
        border: 1px solid rgba(255,107,44,0.4);
        border-radius: 50%;
        top: calc(35% - 8px);
        left: calc(60% - 8px);
        animation: pulse-ring 2s ease-out infinite;
    }

    @keyframes pulse-ring {
        0% { transform: scale(1); opacity: 0.6; }
        100% { transform: scale(2.5); opacity: 0; }
    }

    /* ── Hero Text Overlay ── */
    .hero-text-block {
        text-align: center;
        position: relative;
        z-index: 2;
        max-width: 480px;
    }

    .hero-title {
        font-size: 2.8rem;
        font-weight: 800;
        line-height: 1.1;
        color: #fff;
        margin: 0;
        letter-spacing: -1px;
    }

    .hero-title-accent {
        background: linear-gradient(135deg, #FF6B2C, #FF8F5C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: block;
    }

    .hero-subtitle {
        font-size: 0.95rem;
        color: #888;
        margin-top: 0.75rem;
        line-height: 1.6;
    }

    /* ── Floating Stat Cards ── */
    .float-stats-left {
        display: flex;
        flex-direction: column;
        gap: 12px;
        min-width: 150px;
    }

    .float-stat {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 12px;
        padding: 12px 16px;
        backdrop-filter: blur(10px);
    }

    .float-stat-label {
        font-size: 0.7rem;
        color: #666;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .float-stat-label .dot-live {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #22c55e;
        display: inline-block;
    }

    .float-stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #fff;
        margin-top: 2px;
    }

    .float-stat-change {
        font-size: 0.75rem;
        color: #22c55e;
        font-weight: 600;
    }

    /* ── Live Events Feed ── */
    .live-feed {
        min-width: 200px;
        max-width: 240px;
    }

    .live-feed-title {
        font-size: 0.75rem;
        color: #FF6B2C;
        font-weight: 600;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .live-feed-title::before {
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #FF6B2C;
        display: inline-block;
    }

    .feed-item {
        padding: 8px 0;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }

    .feed-item-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #e0e0e0;
    }

    .feed-item-desc {
        font-size: 0.65rem;
        color: #666;
        margin-top: 1px;
    }

    .feed-item-time {
        font-size: 0.6rem;
        color: #444;
        float: right;
        margin-top: -28px;
    }

    /* ── Quick Pick Countries ── */
    .quick-picks {
        display: flex;
        gap: 8px;
        justify-content: center;
        flex-wrap: wrap;
        margin: 1rem 0;
    }

    .quick-pick-btn {
        background: rgba(255,107,44,0.08);
        border: 1px solid rgba(255,107,44,0.15);
        border-radius: 20px;
        padding: 6px 16px;
        font-size: 0.8rem;
        color: #FF6B2C;
        cursor: pointer;
        transition: all 0.2s;
    }

    .quick-pick-btn:hover {
        background: rgba(255,107,44,0.15);
        border-color: rgba(255,107,44,0.3);
    }

    /* ── Search Bar Styling ── */
    .stTextInput input {
        background: rgba(255,255,255,0.05) !important;
        background-color: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 14px !important;
        padding: 0.9rem 1.2rem !important;
        font-size: 1rem !important;
        color: #FF6B2C !important;
        caret-color: #FF6B2C !important;
        -webkit-text-fill-color: #FF6B2C !important;
    }

    .stTextInput input:focus {
        border-color: rgba(255,107,44,0.4) !important;
        box-shadow: 0 0 20px rgba(255,107,44,0.1) !important;
    }

    .stTextInput input::placeholder {
        color: #555 !important;
        -webkit-text-fill-color: #555 !important;
    }

    /* Fix text input label color */
    .stTextInput label {
        color: #888 !important;
    }

    /* ── Button Styling ── */
    .stButton > button {
        background: linear-gradient(135deg, #FF6B2C 0%, #FF8F5C 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.9rem 2rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 20px rgba(255,107,44,0.3) !important;
    }

    .stButton > button:hover {
        box-shadow: 0 6px 30px rgba(255,107,44,0.5) !important;
        transform: translateY(-1px);
    }

    /* ── Stat Cards Row ── */
    .stat-card-dark {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
    }

    .stat-card-dark h3 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        color: #FF6B2C;
    }

    .stat-card-dark p {
        font-size: 0.8rem;
        color: #666;
        margin: 0.3rem 0 0 0;
    }

    /* ── Briefing Content ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,0.02);
        border-radius: 12px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #888;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background: rgba(255,107,44,0.1) !important;
        color: #FF6B2C !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        background: rgba(255,255,255,0.02);
        border-radius: 14px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.04);
    }

    /* Markdown content inside tabs */
    .stMarkdown h2 {
        color: #FF6B2C !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin-top: 2rem !important;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(255,107,44,0.15);
    }

    .stMarkdown h2:first-child {
        margin-top: 0 !important;
    }

    .stMarkdown strong {
        color: #FF8F5C;
    }

    .stMarkdown a {
        color: #FF6B2C !important;
    }

    /* ── Download Buttons ── */
    .stDownloadButton > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: #ccc !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
    }

    .stDownloadButton > button:hover {
        background: rgba(255,107,44,0.1) !important;
        border-color: rgba(255,107,44,0.3) !important;
        color: #FF6B2C !important;
    }

    /* ── Status widget ── */
    details[data-testid="stExpander"] {
        background: rgba(255,255,255,0.02) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 14px !important;
    }

    /* ── Divider ── */
    .geo-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(255,107,44,0.2), transparent);
        margin: 1.5rem 0;
    }

    /* ── Footer ── */
    .geo-footer {
        text-align: center;
        padding: 1.5rem 0;
        font-size: 0.75rem;
        color: #444;
    }

    .geo-footer a {
        color: #FF6B2C;
        text-decoration: none;
    }

    /* ── Feature Cards ── */
    .feature-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 14px;
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s;
    }

    .feature-card:hover {
        border-color: rgba(255,107,44,0.2);
        background: rgba(255,107,44,0.03);
    }

    .feature-icon {
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }

    .feature-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #fff;
        margin-bottom: 0.3rem;
    }

    .feature-desc {
        font-size: 0.75rem;
        color: #666;
        line-height: 1.5;
    }

    /* ── Sidebar polish ── */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255,107,44,0.08) !important;
        border: 1px solid rgba(255,107,44,0.15) !important;
        color: #FF6B2C !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,107,44,0.15) !important;
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.04) !important;
        border-color: rgba(255,255,255,0.08) !important;
        border-radius: 10px !important;
    }

    /* ── Top countries ── */
    .top-countries {
        margin-top: 1rem;
    }

    .top-country-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid rgba(255,255,255,0.03);
        font-size: 0.8rem;
    }

    .top-country-flag {
        margin-right: 8px;
    }

    .top-country-count {
        color: #FF6B2C;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    anthropic_key = st.text_input(
        "Anthropic API Key",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        type="password",
        help="console.anthropic.com/settings/keys"
    )

    tavily_key = st.text_input(
        "Tavily API Key",
        value=os.environ.get("TAVILY_API_KEY", ""),
        type="password",
        help="tavily.com"
    )

    model = st.selectbox(
        "Model",
        ["claude-sonnet-4-6", "claude-haiku-5-5", "claude-opus-4-6"],
        help="Sonnet = fast & cheap · Haiku = fastest · Opus = deepest"
    )

    st.divider()

    st.markdown("### 🌍 Quick Pick")
    suggestions = ["Iran", "Taiwan", "Ukraine", "Turkey", "India",
                    "Nigeria", "Brazil", "South Korea", "Israel", "Pakistan"]
    for s in suggestions:
        if st.button(s, key=f"sug_{s}", use_container_width=True):
            st.session_state["country_input"] = s

    st.divider()
    st.caption("Built by **Ronak Kaup**")
    st.caption("[LinkedIn](https://linkedin.com/in/ronak-kaup) · [Portfolio](https://ronakkaup.co.uk)")

# ─── Tool Definition ──────────────────────────────────────────────
# ─── Phase 3: Multi-Stage Research Agent ─────────────────────────
# Stage 1 — PLAN: Claude generates targeted sub-queries per topic
# Stage 2 — RESEARCH: Tavily executes all searches
# Stage 3 — SYNTHESISE: Claude writes the briefing from all research

PLANNING_PROMPT = """You are GeoIntel AI's research planner. Given a country, your job is to
generate a set of highly targeted web search queries that will gather the information
needed for a comprehensive geopolitical briefing.

Break the research into these topic areas and generate 2-3 specific search queries per area:

1. **Overview & Government** — official stats, head of state, government structure
2. **Recent Political Developments** — elections, protests, policy changes, coups
3. **Economy & Trade** — GDP, industries, sanctions, trade deals, economic crises
4. **Foreign Relations** — alliances, disputes, diplomacy, regional role
5. **Military & Security** — armed forces, conflicts, nuclear status, terrorism
6. **Current Headlines** — latest news in the past month

RULES:
- Generate 12-15 search queries total (at least 2 per topic area)
- Make queries SPECIFIC — include the country name and specific terms
- Focus on CURRENT information (2024-2026)
- Include at least 2 queries for the most newsworthy/volatile topic area

Respond ONLY with valid JSON in this exact format, no other text:
{
    "topic_queries": [
        {"topic": "Overview & Government", "query": "...", "priority": "high"},
        {"topic": "Economy & Trade", "query": "...", "priority": "medium"},
        ...
    ]
}"""

SYNTHESIS_PROMPT = """You are GeoIntel AI, a geopolitical research analyst.

You have been given raw research data from multiple web searches about a country.
Your job: synthesise ALL of this research into a comprehensive, well-sourced briefing.

OUTPUT FORMAT — use these exact sections:

## 🏛️ Country Overview
Official name, capital, population, region, government type, current head of state/government.

## 📜 Historical Background
Key events that shaped today's political landscape. Focus on the last 100 years.

## ⚖️ Current Political Landscape
Government structure, ruling party, opposition, recent elections, stability assessment.

## 💰 Economy
GDP, major industries, challenges, trade relationships, sanctions if any.

## 🤝 Foreign Relations & Alliances
Key allies, adversaries, regional role, international memberships, ongoing disputes.

## 🛡️ Military & Security
Military strength, nuclear status, active conflicts, internal security threats.

## 🔮 Key Issues to Watch
2-3 current developments that could shift the country's geopolitical position.

## 📋 Bottom Line
A 2-3 sentence executive summary of the country's geopolitical position.

## 🔗 Sources
List every URL you used with a one-line description.

FORMAT RULES:
- Professional but accessible tone (think: BBC World Service briefing)
- Use bullet points for readability
- Cite specific numbers and dates where possible
- Use bold for key figures, organisations, and statistics
- Cross-reference facts across multiple sources where possible
- Flag any contradictions between sources
- If information is sparse on a topic, say so rather than speculating
"""

# Legacy single-pass tools + prompt (kept as fallback for the agent loop path)
TOOLS = [
    {
        "name": "web_search",
        "description": (
            "Search the web for current information on any topic. "
            "Returns relevant results with titles, URLs, and content snippets. "
            "Use this to find up-to-date facts, statistics, news, and analysis."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query. Be specific for better results."
                }
            },
            "required": ["query"]
        }
    }
]


# ─── Tavily Search Helper ────────────────────────────────────────
def tavily_search(query, tavily_client, max_results=5):
    """Execute a single Tavily search and return formatted results."""
    try:
        results = tavily_client.search(
            query=query,
            max_results=max_results,
            include_raw_content=False
        )
        formatted = []
        for r in results.get("results", []):
            formatted.append(
                f"Title: {r['title']}\n"
                f"URL: {r['url']}\n"
                f"Content: {r['content']}"
            )
        return "\n---\n".join(formatted) if formatted else "No results found."
    except Exception as e:
        return f"Search error: {str(e)}"


# ─── Stage 1: Research Planner ───────────────────────────────────
def plan_research(country, claude_client, model_name, status):
    """Ask Claude to generate targeted sub-queries for the country."""
    status.write("🧠 **Stage 1 / 3 — Planning research strategy...**")

    response = claude_client.messages.create(
        model=model_name,
        max_tokens=2048,
        system=PLANNING_PROMPT,
        messages=[
            {"role": "user", "content": f"Generate research queries for: {country}"}
        ]
    )

    raw_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            raw_text = block.text
            break

    # Parse the JSON — handle markdown code fences if present
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        # Remove ```json ... ``` wrapper
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        plan = json.loads(cleaned)
        queries = plan.get("topic_queries", [])
        status.write(f"📋 **Planned {len(queries)} targeted searches across {len(set(q['topic'] for q in queries))} topic areas**")
        return queries
    except json.JSONDecodeError:
        # Fallback: generate default queries if JSON parsing fails
        status.write("⚠️ Planner returned non-JSON — using default research plan")
        return [
            {"topic": "Overview & Government", "query": f"{country} government political system head of state 2026", "priority": "high"},
            {"topic": "Overview & Government", "query": f"{country} population demographics capital city", "priority": "medium"},
            {"topic": "Political Developments", "query": f"{country} latest political news elections 2026", "priority": "high"},
            {"topic": "Political Developments", "query": f"{country} political crisis protests opposition 2025 2026", "priority": "medium"},
            {"topic": "Economy & Trade", "query": f"{country} GDP economy trade 2025 2026", "priority": "high"},
            {"topic": "Economy & Trade", "query": f"{country} economic sanctions trade agreements", "priority": "medium"},
            {"topic": "Foreign Relations", "query": f"{country} foreign policy alliances diplomatic relations 2026", "priority": "high"},
            {"topic": "Foreign Relations", "query": f"{country} territorial disputes conflicts neighbours", "priority": "medium"},
            {"topic": "Military & Security", "query": f"{country} military armed forces defence spending", "priority": "high"},
            {"topic": "Military & Security", "query": f"{country} security threats terrorism conflicts 2026", "priority": "medium"},
            {"topic": "Current Headlines", "query": f"{country} latest news today 2026", "priority": "high"},
            {"topic": "Current Headlines", "query": f"{country} breaking news recent developments", "priority": "medium"},
        ]


# ─── Stage 2: Execute Research ───────────────────────────────────
def execute_research(queries, tavily_client, status):
    """Execute all planned searches and collect results by topic."""
    status.write("🔍 **Stage 2 / 3 — Executing searches...**")

    research_by_topic = {}
    all_searches = []
    search_count = 0

    for q in queries:
        topic = q["topic"]
        query = q["query"]
        priority = q.get("priority", "medium")
        search_count += 1

        # More results for high-priority queries
        max_results = 6 if priority == "high" else 4

        status.write(f"🔍 **Search {search_count}/{len(queries)}** [{topic}]: {query}")
        result = tavily_search(query, tavily_client, max_results=max_results)
        all_searches.append(query)

        if topic not in research_by_topic:
            research_by_topic[topic] = []
        research_by_topic[topic].append({
            "query": query,
            "results": result
        })

    status.write(f"✅ **{search_count} searches complete — compiling research dossier...**")
    return research_by_topic, all_searches, search_count


# ─── Stage 3: Synthesise Briefing ────────────────────────────────
def synthesise_briefing(country, research_by_topic, claude_client, model_name, status):
    """Feed all research to Claude for synthesis into a final briefing."""
    status.write("✍️ **Stage 3 / 3 — Synthesising briefing...**")

    # Build a structured research dossier for Claude
    dossier_parts = [f"# Research Dossier: {country}\n"]
    for topic, searches in research_by_topic.items():
        dossier_parts.append(f"\n## Research Area: {topic}\n")
        for s in searches:
            dossier_parts.append(f"### Query: {s['query']}\n{s['results']}\n")

    dossier = "\n".join(dossier_parts)

    # Truncate if the dossier is extremely long (keep Claude's context manageable)
    max_chars = 90000
    if len(dossier) > max_chars:
        dossier = dossier[:max_chars] + "\n\n[... research truncated for length ...]"

    response = claude_client.messages.create(
        model=model_name,
        max_tokens=8096,
        system=SYNTHESIS_PROMPT,
        messages=[
            {
                "role": "user",
                "content": (
                    f"Here is the complete research dossier for {country}. "
                    f"Synthesise this into a comprehensive geopolitical briefing.\n\n"
                    f"{dossier}"
                )
            }
        ]
    )

    for block in response.content:
        if hasattr(block, "text"):
            return block.text
    return "Error: No text in synthesis response"


# ─── Main Agent Orchestrator ─────────────────────────────────────
def generate_briefing(country, claude_client, tavily_client, model_name):
    """3-stage agent: Plan → Research → Synthesise."""
    status = st.status(f"🌐 Deep-researching {country}...", expanded=True)
    start_time = time.time()

    # Stage 1: Plan
    queries = plan_research(country, claude_client, model_name, status)

    # Stage 2: Research
    research_by_topic, searches, search_count = execute_research(
        queries, tavily_client, status
    )

    # Stage 3: Synthesise
    briefing = synthesise_briefing(
        country, research_by_topic, claude_client, model_name, status
    )

    elapsed = round(time.time() - start_time, 1)
    topic_count = len(research_by_topic)
    status.update(
        label=f"✅ Briefing complete — {search_count} searches across {topic_count} topics in {elapsed}s",
        state="complete"
    )

    return briefing, search_count, elapsed, searches


# ─── Main UI ──────────────────────────────────────────────────────

# Hero Section with Globe — rendered via components.html (iframe) so full HTML works
HERO_HTML = """
<html>
<head>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: transparent; font-family: 'Inter', sans-serif; color: #e0e0e0; overflow: hidden; }

.brand { text-align: center; padding: 0.8rem 0 0.3rem; }
.brand-inner { display: inline-flex; align-items: center; gap: 8px; }
.brand-dot { width: 7px; height: 7px; border-radius: 50%; background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.5); }
.brand-text { font-size: 0.7rem; color: #666; letter-spacing: 2px; text-transform: uppercase; }

.hero { display: flex; align-items: center; justify-content: center; gap: 2.5rem; padding: 0.8rem 1rem 0.5rem; }

.stats { display: flex; flex-direction: column; gap: 12px; min-width: 140px; }
.stat-box { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; padding: 14px 16px; }
.stat-label { font-size: 0.65rem; color: #666; display: flex; align-items: center; gap: 5px; }
.stat-label .dot { width: 5px; height: 5px; border-radius: 50%; background: #22c55e; }
.stat-val { font-size: 1.7rem; font-weight: 700; color: #fff; margin-top: 2px; }
.stat-sub { font-size: 0.7rem; color: #22c55e; font-weight: 600; }

.globe { width: 280px; height: 280px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, rgba(255,107,44,0.12), transparent 60%), radial-gradient(circle at 50% 50%, #0d1117, #080a0f); border: 1px solid rgba(255,107,44,0.15); position: relative; flex-shrink: 0; box-shadow: 0 0 80px rgba(255,107,44,0.08), 0 0 160px rgba(255,107,44,0.03), inset 0 0 60px rgba(0,0,0,0.5); overflow: hidden; }
.globe svg { position: absolute; inset: 0; width: 100%; height: 100%; }
.grid-overlay { position: absolute; inset: 0; border-radius: 50%; background: repeating-linear-gradient(0deg, transparent, transparent 34px, rgba(255,107,44,0.04) 34px, rgba(255,107,44,0.04) 35px), repeating-linear-gradient(90deg, transparent, transparent 34px, rgba(255,107,44,0.04) 34px, rgba(255,107,44,0.04) 35px); z-index: 1; }
.globe-shine { position: absolute; inset: 0; border-radius: 50%; background: radial-gradient(circle at 30% 30%, rgba(255,255,255,0.04), transparent 60%); z-index: 3; pointer-events: none; }

.pin { position: absolute; border-radius: 50%; border: 2px solid #fff; background: #FF6B2C; z-index: 4; }
.p1 { width: 14px; height: 14px; top: 32%; left: 62%; box-shadow: 0 0 16px rgba(255,107,44,0.6); }
.p2 { width: 10px; height: 10px; top: 56%; left: 38%; box-shadow: 0 0 10px rgba(255,107,44,0.5); }
.p3 { width: 10px; height: 10px; top: 22%; left: 42%; box-shadow: 0 0 10px rgba(255,107,44,0.5); }
.p4 { width: 8px; height: 8px; top: 44%; left: 22%; box-shadow: 0 0 8px rgba(255,107,44,0.4); }
.p5 { width: 8px; height: 8px; top: 38%; left: 76%; box-shadow: 0 0 8px rgba(255,107,44,0.4); }

.pulse { position: absolute; width: 30px; height: 30px; border: 1px solid rgba(255,107,44,0.4); border-radius: 50%; top: calc(32% - 8px); left: calc(62% - 8px); animation: pulse-ring 2s ease-out infinite; z-index: 3; }
.pulse2 { position: absolute; width: 24px; height: 24px; border: 1px solid rgba(255,107,44,0.3); border-radius: 50%; top: calc(56% - 7px); left: calc(38% - 7px); animation: pulse-ring 2.5s ease-out infinite 0.5s; z-index: 3; }
@keyframes pulse-ring { 0% { transform: scale(1); opacity: 0.6; } 100% { transform: scale(2.5); opacity: 0; } }

.right-col { max-width: 260px; }
.hero-title { font-size: 2.6rem; font-weight: 800; line-height: 1.1; color: #fff; letter-spacing: -0.5px; }
.accent { display: block; background: linear-gradient(135deg, #FF6B2C, #FF8F5C); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-sub { font-size: 0.85rem; color: #777; margin-top: 0.6rem; line-height: 1.6; }

.feed-title { font-size: 0.7rem; color: #FF6B2C; font-weight: 600; margin: 1rem 0 6px; display: flex; align-items: center; gap: 5px; }
.feed-title::before { content: ''; width: 5px; height: 5px; border-radius: 50%; background: #FF6B2C; }
.feed-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.03); font-size: 0.75rem; color: #ccc; }
.feed-tag { color: #FF6B2C; font-weight: 600; font-size: 0.65rem; }
</style>
</head>
<body>
<div class="brand">
    <div class="brand-inner">
        <span class="brand-dot"></span>
        <span class="brand-text">Live Intelligence System</span>
    </div>
</div>
<div class="hero">
    <div class="stats">
        <div class="stat-box">
            <div class="stat-label"><span class="dot"></span> Active now</div>
            <div class="stat-val">AI</div>
            <div class="stat-sub">agent ready</div>
        </div>
        <div class="stat-box">
            <div class="stat-label">Sources available</div>
            <div class="stat-val">&infin;</div>
            <div class="stat-sub">real-time web</div>
        </div>
    </div>
    <div class="globe">
        <svg viewBox="0 0 280 280" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <clipPath id="globe-clip"><circle cx="140" cy="140" r="139"/></clipPath>
                <radialGradient id="ocean" cx="40%" cy="35%"><stop offset="0%" stop-color="#0f1923"/><stop offset="100%" stop-color="#070b10"/></radialGradient>
            </defs>
            <g clip-path="url(#globe-clip)">
                <circle cx="140" cy="140" r="139" fill="url(#ocean)"/>
                <g fill="rgba(255,107,44,0.18)" stroke="rgba(255,107,44,0.25)" stroke-width="0.5">
                    <path d="M95,28 L105,25 L115,30 L120,22 L132,20 L140,28 L148,26 L155,32 L152,40 L158,48 L150,55 L142,52 L135,56 L128,50 L120,54 L112,48 L105,52 L98,45 L92,38 Z"/>
                    <path d="M160,30 L175,28 L190,35 L200,32 L210,40 L215,55 L208,65 L200,60 L192,66 L185,58 L175,62 L168,55 L162,48 L158,40 Z"/>
                    <path d="M60,65 L72,60 L85,62 L95,58 L108,62 L118,68 L130,65 L142,70 L150,68 L160,74 L168,80 L175,88 L180,98 L178,110 L172,118 L165,125 L155,128 L148,122 L140,130 L130,132 L120,126 L110,130 L100,125 L92,118 L85,112 L78,105 L72,96 L68,88 L62,80 L58,72 Z"/>
                    <path d="M175,78 L185,72 L195,75 L205,70 L218,74 L228,82 L235,92 L240,105 L242,118 L238,130 L232,138 L225,132 L218,140 L210,135 L202,142 L195,138 L188,145 L180,140 L175,132 L170,120 L168,108 L170,96 L172,88 Z"/>
                    <path d="M105,145 L115,140 L128,142 L138,148 L145,155 L150,165 L148,175 L142,182 L135,188 L125,192 L115,195 L108,200 L100,208 L92,215 L85,210 L80,200 L78,190 L82,180 L88,170 L95,160 L100,152 Z"/>
                    <path d="M200,150 L212,148 L222,155 L230,165 L232,178 L228,188 L220,195 L210,198 L200,195 L195,185 L192,172 L195,160 Z"/>
                    <path d="M55,135 L65,130 L75,135 L80,145 L78,155 L72,162 L62,160 L55,152 L52,142 Z"/>
                </g>
                <line x1="0" y1="140" x2="280" y2="140" stroke="rgba(255,107,44,0.06)" stroke-width="0.5"/>
                <ellipse cx="140" cy="140" rx="139" ry="45" fill="none" stroke="rgba(255,107,44,0.05)" stroke-width="0.5"/>
                <ellipse cx="140" cy="140" rx="90" ry="139" fill="none" stroke="rgba(255,107,44,0.05)" stroke-width="0.5"/>
                <ellipse cx="140" cy="140" rx="50" ry="139" fill="none" stroke="rgba(255,107,44,0.05)" stroke-width="0.5"/>
                <ellipse cx="140" cy="140" rx="139" ry="80" fill="none" stroke="rgba(255,107,44,0.04)" stroke-width="0.5"/>
            </g>
        </svg>
        <div class="grid-overlay"></div>
        <div class="globe-shine"></div>
        <div class="pin p1"></div>
        <div class="pin p2"></div>
        <div class="pin p3"></div>
        <div class="pin p4"></div>
        <div class="pin p5"></div>
        <div class="pulse"></div>
        <div class="pulse2"></div>
    </div>
    <div class="right-col">
        <h1 class="hero-title">See Your World<span class="accent">Decoded.</span></h1>
        <p class="hero-sub">AI-powered geopolitical intelligence on any country. Real-time web research, structured briefings, cited sources.</p>
        <div class="feed-title">Top locations</div>
        <div class="feed-row"><span>&#127470;&#127479; Iran</span><span class="feed-tag">Popular</span></div>
        <div class="feed-row"><span>&#127481;&#127484; Taiwan</span><span class="feed-tag">Trending</span></div>
        <div class="feed-row"><span>&#127482;&#127462; Ukraine</span><span class="feed-tag">Active</span></div>
        <div class="feed-row"><span>&#127481;&#127479; Turkey</span><span class="feed-tag">New</span></div>
        <div class="feed-row"><span>&#127470;&#127475; India</span><span class="feed-tag">Rising</span></div>
    </div>
</div>
</body>
</html>
"""
components.html(HERO_HTML, height=420, scrolling=False)

# Search bar
st.markdown('<div style="height:1px;background:linear-gradient(to right,transparent,rgba(255,107,44,0.2),transparent);margin:1rem 0;"></div>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    country = st.text_input(
        "Country",
        value=st.session_state.get("country_input", ""),
        placeholder="🌍 Enter a country — e.g. Turkey, Iran, Taiwan, Ukraine...",
        label_visibility="collapsed"
    )
with col2:
    run_button = st.button("Generate Briefing", type="primary", use_container_width=True)

# Quick pick country buttons
quick_countries = [
    ("🇮🇷", "Iran"), ("🇹🇼", "Taiwan"), ("🇺🇦", "Ukraine"), ("🇹🇷", "Turkey"),
    ("🇮🇳", "India"), ("🇳🇬", "Nigeria"), ("🇧🇷", "Brazil"), ("🇰🇷", "South Korea"),
    ("🇮🇱", "Israel"), ("🇵🇰", "Pakistan")
]
# Inject per-button override CSS right before the chips (most reliable Streamlit targeting)
st.markdown("""
<style>
    /* Target chip buttons by their key-based data attribute */
    button[data-testid="stBaseButton-secondary"][kind="secondary"] {
        background: rgba(255,107,44,0.08) !important;
        border: 1px solid rgba(255,107,44,0.2) !important;
        color: #FF6B2C !important;
        border-radius: 20px !important;
        padding: 0.35rem 0.6rem !important;
        font-size: 0.75rem !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        letter-spacing: 0 !important;
        min-height: 0 !important;
        line-height: 1.2 !important;
    }
    button[data-testid="stBaseButton-secondary"][kind="secondary"]:hover {
        background: rgba(255,107,44,0.15) !important;
        border-color: rgba(255,107,44,0.4) !important;
        box-shadow: none !important;
        transform: none !important;
    }
</style>
""", unsafe_allow_html=True)
chip_cols = st.columns(len(quick_countries))
for i, (flag, name) in enumerate(quick_countries):
    with chip_cols[i]:
        if st.button(f"{flag} {name}", key=f"chip_{name}", use_container_width=True):
            st.session_state["country_input"] = name
            st.session_state["auto_run"] = True
            st.rerun()

st.markdown('<div style="height:1px;background:linear-gradient(to right,transparent,rgba(255,107,44,0.2),transparent);margin:1rem 0;"></div>', unsafe_allow_html=True)

# ─── Run ──────────────────────────────────────────────────────────
# Check if we should auto-run from a chip click
auto_run = st.session_state.pop("auto_run", False)
if (run_button or auto_run) and country:
    if not anthropic_key or not tavily_key:
        st.error("⚠️ Please enter both API keys in the sidebar (click ☰ top-left).")
    else:
        claude_client = anthropic.Anthropic(api_key=anthropic_key)
        tavily_client = TavilyClient(api_key=tavily_key)

        briefing, search_count, elapsed, searches = generate_briefing(
            country, claude_client, tavily_client, model
        )

        # Stats row
        stat_style = "background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:14px;padding:1.2rem;text-align:center;"
        h3_style = "font-size:2rem;font-weight:700;margin:0;color:#FF6B2C;"
        p_style = "font-size:0.8rem;color:#666;margin:0.3rem 0 0 0;"

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div style="{stat_style}"><h3 style="{h3_style}">{search_count}</h3><p style="{p_style}">Web Searches</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div style="{stat_style}"><h3 style="{h3_style}">{elapsed}s</h3><p style="{p_style}">Research Time</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div style="{stat_style}"><h3 style="{h3_style}">{len(briefing.split())}</h3><p style="{p_style}">Words Generated</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div style="{stat_style}"><h3 style="{h3_style}">{len(searches)}</h3><p style="{p_style}">Sources Found</p></div>', unsafe_allow_html=True)

        st.markdown("")

        # Briefing in tabs
        tab1, tab2 = st.tabs(["📄 Intelligence Briefing", "🔍 Search Log"])

        with tab1:
            st.markdown(briefing)

        with tab2:
            st.markdown("### Searches performed by the AI agent:")
            for i, q in enumerate(searches, 1):
                st.markdown(f"**{i}.** `{q}`")

        # Download section
        st.markdown('<div style="height:1px;background:linear-gradient(to right,transparent,rgba(255,107,44,0.2),transparent);margin:1.5rem 0;"></div>', unsafe_allow_html=True)

        dl_col1, dl_col2, dl_col3 = st.columns([1, 1, 2])
        with dl_col1:
            st.download_button(
                label="📥 Download Markdown",
                data=f"# GeoIntel AI Briefing: {country}\n\n{briefing}",
                file_name=f"geointel_{country.lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with dl_col2:
            st.download_button(
                label="📄 Download Text",
                data=briefing,
                file_name=f"geointel_{country.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

elif run_button and not country:
    st.warning("Please enter a country name.")

# ─── Empty State (before search) ─────────────────────────────────
if not run_button:
    FEATURES_HTML = """
    <html><head><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet"><style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: transparent; font-family: 'Inter', sans-serif; display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 4px; }
    .card { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); border-radius: 14px; padding: 1.3rem; text-align: center; }
    .icon { font-size: 1.6rem; margin-bottom: 0.4rem; }
    .title { font-size: 0.85rem; font-weight: 600; color: #fff; margin-bottom: 0.3rem; }
    .desc { font-size: 0.72rem; color: #666; line-height: 1.5; }
    </style></head><body>
    <div class="card"><div class="icon">&#128269;</div><div class="title">Real-time research</div><div class="desc">Searches the live web &mdash; not just AI memory. Gets current data, news, and stats.</div></div>
    <div class="card"><div class="icon">&#128202;</div><div class="title">Structured briefings</div><div class="desc">8 sections covering politics, economy, military, diplomacy, and outlook.</div></div>
    <div class="card"><div class="icon">&#128279;</div><div class="title">Cited sources</div><div class="desc">Every claim backed by a URL you can verify. Full transparency.</div></div>
    </body></html>
    """
    components.html(FEATURES_HTML, height=140, scrolling=False)

# ─── Footer ──────────────────────────────────────────────────────
st.markdown('<div style="height:1px;background:linear-gradient(to right,transparent,rgba(255,107,44,0.2),transparent);margin:1.5rem 0;"></div>', unsafe_allow_html=True)
FOOTER_HTML = """
<html><head><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400&display=swap" rel="stylesheet"><style>
* { margin: 0; padding: 0; }
body { background: transparent; font-family: 'Inter', sans-serif; text-align: center; padding: 0.5rem 0; font-size: 0.75rem; color: #444; }
a { color: #FF6B2C; text-decoration: none; }
</style></head><body>
GeoIntel AI &middot; Built by <a href="https://ronakkaup.co.uk" target="_blank">Ronak Kaup</a>
&middot; Powered by <a href="https://anthropic.com" target="_blank">Claude AI</a>
+ <a href="https://tavily.com" target="_blank">Tavily</a>
<br>
<a href="https://linkedin.com/in/ronak-kaup" target="_blank">LinkedIn</a>
&middot; <a href="https://github.com/ronakkaup" target="_blank">GitHub</a>
</body></html>
"""
components.html(FOOTER_HTML, height=55, scrolling=False)
