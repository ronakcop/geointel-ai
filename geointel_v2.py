"""
GeoIntel AI — Phase 2: The Agent (With Web Search!)
====================================================
This version adds TOOL USE — Claude can now search the web using Tavily.

THE BIG DIFFERENCE FROM PHASE 1:
- Phase 1: One call to Claude → one answer (from memory)
- Phase 2: Claude LOOPS — it thinks, searches the web, reads results,
           searches again, and keeps going until it has enough info.

This is what makes it an "agent" — Claude decides WHAT to search and
WHEN to stop, not you.

WHAT YOU'RE LEARNING:
- How LLM "tool use" / "function calling" works
- The agent loop pattern (the foundation of ALL AI agents)
- How to wire up an external API (Tavily) as a tool
"""

import anthropic
import json
import sys
from tavily import TavilyClient

# ─── Step 1: Create both clients ──────────────────────────────────
# We now have TWO APIs:
#   - Anthropic (Claude) = the brain that thinks and writes
#   - Tavily = the search engine that finds real-time info
#
# Set both keys in PowerShell before running:
#   $env:ANTHROPIC_API_KEY="sk-ant-..."
#   $env:TAVILY_API_KEY="tvly-..."

claude = anthropic.Anthropic()
tavily = TavilyClient()  # Reads TAVILY_API_KEY from environment

# ─── Step 2: Define the Tool ──────────────────────────────────────
# This is the KEY CONCEPT of Phase 2: TOOL DEFINITION.
#
# You're telling Claude: "Hey, you have access to a web search tool.
# Here's what it's called, what it does, and what parameters it takes."
#
# Claude doesn't actually RUN the search — it ASKS you to run it.
# The flow is:
#   1. Claude says: "I want to call web_search with query='Turkey economy 2024'"
#   2. YOUR CODE runs the actual Tavily search
#   3. You send the results BACK to Claude
#   4. Claude reads them and decides what to do next
#
# This is called "function calling" or "tool use" — same thing.

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

# ─── Step 3: The System Prompt (upgraded) ─────────────────────────
# Same structure as Phase 1, but now we tell Claude it HAS web search
# and should USE it to get current, cited information.

SYSTEM_PROMPT = """You are GeoIntel AI, a geopolitical research analyst with access to web search.

Your job: when given a country name, produce a comprehensive, SOURCED geopolitical briefing.

RESEARCH PROCESS:
1. Search for the country's current political situation
2. Search for economic data and trade relationships
3. Search for military/security situation and conflicts
4. Search for recent news and developments
5. Synthesise everything into a structured briefing

You MUST use the web_search tool multiple times to gather current information.
Do NOT rely on your training knowledge alone — search for real, current data.
Aim for 5-8 searches to cover all angles.

OUTPUT FORMAT — use these exact sections:

1. **Country Overview** — Official name, capital, population, region,
   government type, current head of state/government.

2. **Historical Background** — Key events that shaped today's political
   landscape. Focus on the last 100 years.

3. **Current Political Landscape** — Government structure, ruling party,
   opposition, recent elections, stability assessment.

4. **Economy** — GDP, major industries, challenges, trade relationships,
   sanctions if any.

5. **Foreign Relations & Alliances** — Key allies, adversaries, regional role,
   international memberships, ongoing disputes.

6. **Military & Security** — Military strength, nuclear status, active
   conflicts, internal security threats.

7. **Key Issues to Watch** — 2-3 current developments that could shift
   the country's geopolitical position.

8. **Sources** — List every URL you used, with a one-line description of
   what you found there.

FORMAT RULES:
- Professional but accessible tone (think: BBC World Service briefing)
- Use bullet points for readability
- Cite specific numbers and dates where possible
- End with a 2-sentence "Bottom Line" summary BEFORE the sources
"""

# ─── Step 4: Execute the tool ─────────────────────────────────────
# When Claude asks to use web_search, THIS function actually runs it.
# It calls Tavily, gets results, and formats them for Claude to read.

def execute_tool(tool_name: str, tool_input: dict) -> str:
    """Run a tool and return the results as a string."""

    if tool_name == "web_search":
        query = tool_input["query"]
        print(f"   🔍 Searching: {query}")

        # Call Tavily API
        results = tavily.search(
            query=query,
            max_results=5,           # Top 5 results per search
            include_raw_content=False # Just snippets, not full pages
        )

        # Format results for Claude to read
        formatted = []
        for r in results.get("results", []):
            formatted.append(
                f"Title: {r['title']}\n"
                f"URL: {r['url']}\n"
                f"Content: {r['content']}\n"
            )

        return "\n---\n".join(formatted) if formatted else "No results found."

    return f"Unknown tool: {tool_name}"


# ─── Step 5: THE AGENT LOOP ──────────────────────────────────────
# This is the CORE PATTERN of AI agents. Understand this and you
# understand how every agent works (AutoGPT, CrewAI, LangChain, etc.)
#
# The loop:
#   1. Send message to Claude
#   2. Claude responds with EITHER:
#      a) A text response (it's done thinking) → EXIT the loop
#      b) A tool_use request (it wants to search) → run the tool,
#         send results back, and GO TO step 1
#
# Claude decides when to search and when to stop. That's agency.

def generate_briefing(country: str) -> str:
    """The agent loop — Claude searches, reads, and writes."""

    print(f"\n🌍 GeoIntel AI — Generating briefing for: {country}")
    print("=" * 50)

    # Start the conversation
    messages = [
        {
            "role": "user",
            "content": f"Generate a full geopolitical briefing for: {country}"
        }
    ]

    search_count = 0

    # THE AGENT LOOP
    while True:
        # Call Claude
        response = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,              # Tell Claude about available tools
            messages=messages
        )

        # Check what Claude wants to do
        if response.stop_reason == "tool_use":
            # Claude wants to use a tool — find which one(s)
            # A single response can contain BOTH text and tool calls

            assistant_content = response.content  # Could be text + tool_use blocks
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    search_count += 1
                    # Run the tool
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            # Add Claude's response and tool results to conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        elif response.stop_reason == "end_turn":
            # Claude is done — extract the final text
            print(f"\n✅ Research complete! ({search_count} web searches performed)")
            print("=" * 50 + "\n")

            # Get the text from the response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

            return "Error: No text in response"

        else:
            # Unexpected stop reason
            print(f"⚠️ Unexpected stop: {response.stop_reason}")
            break

    return "Error: Agent loop ended unexpectedly"


# ─── Step 6: Run it ───────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        country = " ".join(sys.argv[1:])
    else:
        country = input("🌍 Enter a country name: ")

    briefing = generate_briefing(country)
    print(briefing)

    # Save to file
    filename = f"briefing_{country.lower().replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# GeoIntel AI Briefing: {country}\n\n")
        f.write(briefing)

    print(f"\n📄 Briefing saved to: {filename}")
