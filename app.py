"""
GeoIntel AI — Streamlit App (Clean Editorial Theme)
=====================================================
AI-powered geopolitical intelligence briefings.
Run with: python -m streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import anthropic
from tavily import TavilyClient
import os
import time
import json
import base64

# ─── Page Config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="GeoIntel AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Logo (base64-embedded) ──────────────────────────────────────
LOGO_B64 = ""
logo_path = os.path.join(os.path.dirname(__file__), "logo_b64.txt")
if os.path.exists(logo_path):
    with open(logo_path) as f:
        LOGO_B64 = f.read().strip()

# ─── Country code mapping for flag images ────────────────────────
COUNTRY_CODES = {
    "Iran": "ir", "Taiwan": "tw", "Ukraine": "ua", "Turkey": "tr",
    "India": "in", "Nigeria": "ng", "Brazil": "br", "South Korea": "kr",
    "Israel": "il", "Pakistan": "pk", "China": "cn", "Russia": "ru",
    "United States": "us", "United Kingdom": "gb", "Japan": "jp",
    "Germany": "de", "France": "fr", "Saudi Arabia": "sa", "Egypt": "eg",
    "Mexico": "mx", "Indonesia": "id", "Philippines": "ph", "Thailand": "th",
    "Vietnam": "vn", "Poland": "pl", "Spain": "es", "Italy": "it",
    "Canada": "ca", "Australia": "au", "South Africa": "za", "Argentina": "ar",
    "Colombia": "co", "Chile": "cl", "Peru": "pe", "Venezuela": "ve",
    "Cuba": "cu", "North Korea": "kp", "Myanmar": "mm", "Afghanistan": "af",
    "Iraq": "iq", "Syria": "sy", "Lebanon": "lb", "Jordan": "jo",
    "Ethiopia": "et", "Kenya": "ke", "Ghana": "gh", "Morocco": "ma",
    "Tunisia": "tn", "Algeria": "dz", "Libya": "ly", "Sudan": "sd",
    "Somalia": "so", "Yemen": "ye", "Oman": "om", "Qatar": "qa",
    "Kuwait": "kw", "Bahrain": "bh", "UAE": "ae",
    "United Arab Emirates": "ae", "Bangladesh": "bd", "Sri Lanka": "lk",
    "Nepal": "np", "Malaysia": "my", "Singapore": "sg", "New Zealand": "nz",
    "Sweden": "se", "Norway": "no", "Denmark": "dk", "Finland": "fi",
    "Netherlands": "nl", "Belgium": "be", "Switzerland": "ch",
    "Austria": "at", "Greece": "gr", "Portugal": "pt", "Ireland": "ie",
    "Czech Republic": "cz", "Hungary": "hu", "Romania": "ro",
    "Bulgaria": "bg", "Serbia": "rs", "Croatia": "hr", "Slovakia": "sk",
    "Slovenia": "si", "Bosnia": "ba", "Kosovo": "xk", "Albania": "al",
    "Moldova": "md", "Belarus": "by", "Georgia": "ge", "Armenia": "am",
    "Azerbaijan": "az", "Kazakhstan": "kz", "Uzbekistan": "uz",
    "Turkmenistan": "tm", "Kyrgyzstan": "kg", "Tajikistan": "tj",
    "Mongolia": "mn", "Taiwan": "tw", "Hong Kong": "hk",
}

def get_flag_url(country_name, width=40):
    """Get flag image URL from flagcdn.com."""
    code = COUNTRY_CODES.get(country_name, "").lower()
    if code:
        return f"https://flagcdn.com/w{width}/{code}.png"
    return ""

def get_flag_html(country_name, width=28, height=20):
    """Get an <img> tag for the country flag, or empty string if not found."""
    url = get_flag_url(country_name, width)
    if url:
        return f'<img src="{url}" width="{width}" height="{height}" style="border-radius:3px;vertical-align:middle;object-fit:cover;" alt="{country_name} flag">'
    return ""


# ─── Custom CSS — Clean Editorial Theme ──────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Global Reset ── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Hide Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Light Background ── */
    .stApp {
        background: #FAFAF9;
        color: #1C1917;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: #F5F5F4;
        border-right: 1px solid #E7E5E4;
    }

    section[data-testid="stSidebar"] * {
        color: #44403C !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(37,99,235,0.06) !important;
        border: 1px solid rgba(37,99,235,0.15) !important;
        color: #2563EB !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(37,99,235,0.12) !important;
    }

    /* ── Search Bar ── */
    .stTextInput input {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D6D3D1 !important;
        border-radius: 10px !important;
        padding: 0.85rem 1.1rem !important;
        font-size: 0.95rem !important;
        color: #1C1917 !important;
        caret-color: #2563EB !important;
        -webkit-text-fill-color: #1C1917 !important;
    }

    .stTextInput input:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
    }

    .stTextInput input::placeholder {
        color: #A8A29E !important;
        -webkit-text-fill-color: #A8A29E !important;
    }

    .stTextInput label {
        color: #78716C !important;
    }

    /* ── Primary Button ── */
    .stButton > button[kind="primary"],
    .stButton > button[data-testid="stBaseButton-primary"] {
        background: #1C1917 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.85rem 1.8rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0 !important;
        transition: all 0.2s !important;
        box-shadow: none !important;
    }

    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-testid="stBaseButton-primary"]:hover {
        background: #292524 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.12) !important;
    }

    /* ── Chip Buttons ── */
    button[data-testid="stBaseButton-secondary"][kind="secondary"] {
        background: #FFFFFF !important;
        border: 1px solid #E7E5E4 !important;
        color: #44403C !important;
        border-radius: 20px !important;
        padding: 0.4rem 0.7rem !important;
        font-size: 0.78rem !important;
        font-weight: 400 !important;
        box-shadow: none !important;
        letter-spacing: 0 !important;
        min-height: 0 !important;
        line-height: 1.3 !important;
        transition: all 0.15s !important;
    }

    button[data-testid="stBaseButton-secondary"][kind="secondary"]:hover {
        background: rgba(37,99,235,0.04) !important;
        border-color: #2563EB !important;
        color: #2563EB !important;
        box-shadow: none !important;
        transform: none !important;
    }

    /* ── Stat Cards ── */
    .stat-card-editorial {
        background: #F5F5F4;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }

    .stat-card-editorial h3 {
        font-size: 1.6rem;
        font-weight: 600;
        margin: 0;
        color: #2563EB;
    }

    .stat-card-editorial p {
        font-size: 0.75rem;
        color: #78716C;
        margin: 0.2rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #F5F5F4;
        border-radius: 10px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #78716C;
        font-weight: 500;
        font-size: 0.85rem;
    }

    .stTabs [aria-selected="true"] {
        background: #FFFFFF !important;
        color: #1C1917 !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }

    .stTabs [data-baseweb="tab-panel"] {
        background: #FFFFFF;
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #E7E5E4;
    }

    /* ── Markdown in briefing ── */
    .stMarkdown h2 {
        color: #1C1917 !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        margin-top: 1.8rem !important;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #E7E5E4;
    }

    .stMarkdown h2:first-child {
        margin-top: 0 !important;
    }

    .stMarkdown strong {
        color: #1C1917;
        font-weight: 600;
    }

    .stMarkdown a {
        color: #2563EB !important;
    }

    /* ── Download Buttons ── */
    .stDownloadButton > button {
        background: #FFFFFF !important;
        border: 1px solid #E7E5E4 !important;
        color: #44403C !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }

    .stDownloadButton > button:hover {
        background: rgba(37,99,235,0.04) !important;
        border-color: #2563EB !important;
        color: #2563EB !important;
    }

    /* ── Status widget ── */
    details[data-testid="stExpander"] {
        background: #FFFFFF !important;
        border: 1px solid #E7E5E4 !important;
        border-radius: 10px !important;
    }

    /* ── Selectbox ── */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
        border-color: #D6D3D1 !important;
        border-radius: 10px !important;
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

    st.markdown("### 🌍 Quick pick")
    suggestions = ["Iran", "Taiwan", "Ukraine", "Turkey", "India",
                    "Nigeria", "Brazil", "South Korea", "Israel", "Pakistan"]
    for s in suggestions:
        if st.button(s, key=f"sug_{s}", use_container_width=True):
            st.session_state["country_input"] = s

    st.divider()
    st.caption("Built by **Ronak Kaup**")
    st.caption("[LinkedIn](https://linkedin.com/in/ronak-kaup) · [Portfolio](https://ronakkaup.co.uk)")


# ─── Phase 3: Multi-Stage Research Agent ─────────────────────────
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

    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    try:
        plan = json.loads(cleaned)
        queries = plan.get("topic_queries", [])
        status.write(f"📋 **Planned {len(queries)} targeted searches across {len(set(q['topic'] for q in queries))} topic areas**")
        return queries
    except json.JSONDecodeError:
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

    dossier_parts = [f"# Research Dossier: {country}\n"]
    for topic, searches in research_by_topic.items():
        dossier_parts.append(f"\n## Research Area: {topic}\n")
        for s in searches:
            dossier_parts.append(f"### Query: {s['query']}\n{s['results']}\n")

    dossier = "\n".join(dossier_parts)

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
    status = st.status(f"Researching {country}...", expanded=True)
    start_time = time.time()

    queries = plan_research(country, claude_client, model_name, status)
    research_by_topic, searches, search_count = execute_research(
        queries, tavily_client, status
    )
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


# ═══════════════════════════════════════════════════════════════════
# MAIN UI — Clean Editorial Layout
# ═══════════════════════════════════════════════════════════════════

# ─── Header ──────────────────────────────────────────────────────
header_left, header_right = st.columns([4, 1])
with header_left:
    logo_col, text_col = st.columns([0.08, 0.92])
    with logo_col:
        if LOGO_B64:
            logo_bytes = base64.b64decode(LOGO_B64)
            st.image(logo_bytes, width=48)
    with text_col:
        st.markdown("""
        <div style="padding-top:2px;">
            <div style="font-size:1.35rem;font-weight:600;color:#1C1917;line-height:1.2;">GeoIntel AI</div>
            <div style="font-size:0.8rem;color:#78716C;">AI-powered geopolitical intelligence briefings</div>
        </div>
        """, unsafe_allow_html=True)
with header_right:
    st.markdown("""
    <div style="text-align:right;padding-top:10px;">
        <span style="font-size:0.72rem;color:#A8A29E;background:#F5F5F4;border:1px solid #E7E5E4;border-radius:16px;padding:5px 14px;">
            Powered by Claude AI + Tavily
        </span>
    </div>
    """, unsafe_allow_html=True)
st.markdown('<div style="height:1px;background:#E7E5E4;margin:0 0 1.2rem;"></div>', unsafe_allow_html=True)

# ─── Search bar ──────────────────────────────────────────────────
st.markdown('<p style="font-size:0.72rem;font-weight:500;color:#78716C;letter-spacing:0.5px;text-transform:uppercase;margin-bottom:0.3rem;">Country</p>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])
with col1:
    country = st.text_input(
        "Country",
        value=st.session_state.get("country_input", ""),
        placeholder="Enter a country name — e.g. Iran, Taiwan, Ukraine...",
        label_visibility="collapsed"
    )
with col2:
    run_button = st.button("Generate briefing", type="primary", use_container_width=True)

# ─── Quick pick country chips with flag images ───────────────────
quick_countries = [
    "Iran", "Taiwan", "Ukraine", "Turkey", "India",
    "Nigeria", "Brazil", "South Korea", "Israel", "Pakistan"
]

chip_cols = st.columns(len(quick_countries))
for i, name in enumerate(quick_countries):
    with chip_cols[i]:
        flag_url = get_flag_url(name, 20)
        # We use the flag emoji as fallback in the button text
        code = COUNTRY_CODES.get(name, "")
        if st.button(f"{name}", key=f"chip_{name}", use_container_width=True):
            st.session_state["country_input"] = name
            st.session_state["auto_run"] = True
            st.rerun()

# Show flag images as a visual row below chips using components.html (st.markdown strips <img>)
flag_row_html = '<div style="display:flex;gap:12px;justify-content:center;padding:4px 0;flex-wrap:wrap;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;">'
for name in quick_countries:
    flag_html = get_flag_html(name, 24, 16)
    if flag_html:
        flag_row_html += f'<div style="display:flex;align-items:center;gap:4px;font-size:0.7rem;color:#78716C;">{flag_html} {name}</div>'
flag_row_html += '</div>'
components.html(flag_row_html, height=30, scrolling=False)

st.markdown('<div style="height:1px;background:#E7E5E4;margin:0.5rem 0 1rem;"></div>', unsafe_allow_html=True)

# ─── Run ──────────────────────────────────────────────────────────
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

        # Country flag + name header (use components.html for <img> tag)
        flag_header = get_flag_html(country, 36, 24)
        if flag_header:
            components.html(f"""
            <div style="display:flex;align-items:center;gap:12px;padding:4px 0;font-family:Inter,-apple-system,BlinkMacSystemFont,sans-serif;">
                {flag_header}
                <span style="font-size:1.3rem;font-weight:600;color:#1C1917;">{country}</span>
                <span style="font-size:0.75rem;color:#A8A29E;">Briefing generated · {time.strftime("%B %Y")}</span>
            </div>
            """, height=45, scrolling=False)
        else:
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:12px;margin:0.5rem 0 1rem;">
                <span style="font-size:1.3rem;font-weight:600;color:#1C1917;">{country}</span>
                <span style="font-size:0.75rem;color:#A8A29E;">Briefing generated · {time.strftime("%B %Y")}</span>
            </div>
            """, unsafe_allow_html=True)

        # Stats row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="stat-card-editorial"><h3>{search_count}</h3><p>Sources</p></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card-editorial"><h3>{elapsed}s</h3><p>Generated</p></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card-editorial"><h3>{len(briefing.split())}</h3><p>Words</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="stat-card-editorial"><h3>9</h3><p>Sections</p></div>', unsafe_allow_html=True)

        st.markdown("")

        # Pipeline progress indicator
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;justify-content:center;padding:0.6rem 0;margin-bottom:0.8rem;">
            <div style="display:flex;align-items:center;gap:6px;">
                <div style="width:22px;height:22px;border-radius:50%;background:#2563EB;color:#fff;font-size:11px;display:flex;align-items:center;justify-content:center;font-weight:500;">1</div>
                <span style="font-size:0.75rem;color:#1C1917;font-weight:500;">Plan</span>
            </div>
            <div style="width:32px;height:1px;background:#D6D3D1;"></div>
            <div style="display:flex;align-items:center;gap:6px;">
                <div style="width:22px;height:22px;border-radius:50%;background:#2563EB;color:#fff;font-size:11px;display:flex;align-items:center;justify-content:center;font-weight:500;">2</div>
                <span style="font-size:0.75rem;color:#1C1917;font-weight:500;">Research</span>
            </div>
            <div style="width:32px;height:1px;background:#D6D3D1;"></div>
            <div style="display:flex;align-items:center;gap:6px;">
                <div style="width:22px;height:22px;border-radius:50%;background:#2563EB;color:#fff;font-size:11px;display:flex;align-items:center;justify-content:center;font-weight:500;">3</div>
                <span style="font-size:0.75rem;color:#1C1917;font-weight:500;">Synthesise</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Briefing in tabs
        tab1, tab2 = st.tabs(["📄 Full briefing", "🔍 Research log"])

        with tab1:
            st.markdown(briefing)

        with tab2:
            st.markdown("### Searches performed by the AI agent:")
            for i, q in enumerate(searches, 1):
                st.markdown(f"**{i}.** `{q}`")

        # Download section
        st.markdown('<div style="height:1px;background:#E7E5E4;margin:1.5rem 0;"></div>', unsafe_allow_html=True)

        dl_col1, dl_col2, dl_col3 = st.columns([1, 1, 2])
        with dl_col1:
            st.download_button(
                label="📥 Download markdown",
                data=f"# GeoIntel AI Briefing: {country}\n\n{briefing}",
                file_name=f"geointel_{country.lower().replace(' ', '_')}.md",
                mime="text/markdown",
                use_container_width=True
            )
        with dl_col2:
            st.download_button(
                label="📄 Download text",
                data=briefing,
                file_name=f"geointel_{country.lower().replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

elif run_button and not country:
    st.warning("Please enter a country name.")

# ─── Empty State (before search) ─────────────────────────────────
if not run_button and not auto_run:
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:0.5rem 0 1.5rem;">
        <div style="background:#FFFFFF;border:1px solid #E7E5E4;border-radius:12px;padding:1.5rem;text-align:center;">
            <div style="font-size:1.5rem;margin-bottom:0.4rem;">🔍</div>
            <div style="font-size:0.85rem;font-weight:500;color:#1C1917;margin-bottom:0.3rem;">Real-time research</div>
            <div style="font-size:0.72rem;color:#78716C;line-height:1.5;">Searches the live web — not just AI memory. Gets current data, news, and stats.</div>
        </div>
        <div style="background:#FFFFFF;border:1px solid #E7E5E4;border-radius:12px;padding:1.5rem;text-align:center;">
            <div style="font-size:1.5rem;margin-bottom:0.4rem;">📊</div>
            <div style="font-size:0.85rem;font-weight:500;color:#1C1917;margin-bottom:0.3rem;">Structured briefings</div>
            <div style="font-size:0.72rem;color:#78716C;line-height:1.5;">9 sections covering politics, economy, military, diplomacy, and outlook.</div>
        </div>
        <div style="background:#FFFFFF;border:1px solid #E7E5E4;border-radius:12px;padding:1.5rem;text-align:center;">
            <div style="font-size:1.5rem;margin-bottom:0.4rem;">🔗</div>
            <div style="font-size:0.85rem;font-weight:500;color:#1C1917;margin-bottom:0.3rem;">Cited sources</div>
            <div style="font-size:0.72rem;color:#78716C;line-height:1.5;">Every claim backed by a URL you can verify. Full transparency.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────
st.markdown(f"""
<div style="text-align:center;padding:1.2rem 0 0.5rem;font-size:0.75rem;color:#A8A29E;border-top:1px solid #E7E5E4;margin-top:1rem;">
    GeoIntel AI · Built by <a href="https://ronakkaup.co.uk" target="_blank" style="color:#2563EB;text-decoration:none;">Ronak Kaup</a>
    · Powered by <a href="https://anthropic.com" target="_blank" style="color:#2563EB;text-decoration:none;">Claude AI</a>
    + <a href="https://tavily.com" target="_blank" style="color:#2563EB;text-decoration:none;">Tavily</a>
    <br>
    <a href="https://linkedin.com/in/ronak-kaup" target="_blank" style="color:#2563EB;text-decoration:none;">LinkedIn</a>
    · <a href="https://github.com/ronakcop" target="_blank" style="color:#2563EB;text-decoration:none;">GitHub</a>
</div>
""", unsafe_allow_html=True)
