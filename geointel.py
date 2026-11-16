"""
GeoIntel AI — Phase 1: The Brain (No Tools Yet)
================================================
This is the simplest version. We send a country name to Claude,
and it writes a geopolitical briefing from its own knowledge.

No web search yet — that's Phase 2. Right now we're just getting
the "skeleton" right: the structure, the system prompt, and the
output format.

WHAT YOU'RE LEARNING:
- How to call the Claude API with the Anthropic Python SDK
- What a "system prompt" is and why it matters
- How to get structured output from an LLM
"""

import anthropic
import json
import sys

# ─── Step 1: Create the client ────────────────────────────────────
# This connects to the Claude API. You'll need an API key.
# Get one at: https://console.anthropic.com/settings/keys
#
# NEVER hardcode your API key in the script. Use an environment variable:
#   export ANTHROPIC_API_KEY="sk-ant-..."
#
# The SDK automatically reads ANTHROPIC_API_KEY from your environment.
client = anthropic.Anthropic()

# ─── Step 2: The System Prompt ─────────────────────────────────────
# This is the most important part of any AI agent.
# Think of it as the "job description" you give your research intern.
# It tells Claude WHO it is, WHAT to produce, and HOW to format it.
#
# A bad system prompt = a confused intern who writes random stuff.
# A good system prompt = a focused analyst who delivers exactly what you need.

SYSTEM_PROMPT = """You are GeoIntel AI, a geopolitical research analyst.

When given a country name, produce a comprehensive geopolitical briefing
with the following sections:

1. **Country Overview** — Official name, capital, population, region,
   government type, current head of state/government.

2. **Historical Background** — Key historical events that shaped the
   country's current political landscape. Focus on the last 100 years.
   Cover independence, major wars, revolutions, regime changes.

3. **Current Political Landscape** — Current government structure,
   ruling party/coalition, major opposition, recent elections,
   political stability assessment.

4. **Economy** — GDP, major industries, economic challenges,
   trade relationships, sanctions if any.

5. **Foreign Relations & Alliances** — Key allies, adversaries,
   regional role, membership in international organisations
   (NATO, EU, BRICS, etc.), ongoing disputes.

6. **Military & Security** — Military strength overview,
   nuclear status, active conflicts, internal security threats.

7. **Key Issues to Watch** — 2-3 current developments that could
   shift the country's geopolitical position.

FORMAT RULES:
- Write in a professional but accessible tone (think: BBC World Service)
- Use bullet points for quick-scan readability
- Keep each section concise — quality over quantity
- End with a 2-sentence "Bottom Line" summary

NOTE: In this version you're working from your training knowledge only.
Be transparent about what you know and flag anything that may be outdated.
"""

# ─── Step 3: The function that calls Claude ────────────────────────
# This is the actual API call. Right now it's a single call —
# "one-shot" — not an agent loop yet. That comes in Phase 2.

def generate_briefing(country: str) -> str:
    """Send a country name to Claude and get a geopolitical briefing back."""

    print(f"\n🌍 Generating briefing for: {country}")
    print("⏳ Thinking...\n")

    # The API call — this is where the magic happens
    message = client.messages.create(
        model="claude-sonnet-4-6",            # From your account's available models
        max_tokens=4096,                     # Max length of the response
        system=SYSTEM_PROMPT,                # The "job description"
        messages=[                           # The conversation
            {
                "role": "user",
                "content": f"Generate a full geopolitical briefing for: {country}"
            }
        ]
    )

    # Extract the text from Claude's response
    # The API returns a structured object; the actual text is inside
    # message.content[0].text
    return message.content[0].text


# ─── Step 4: Run it ───────────────────────────────────────────────
# Simple command-line interface. Run with:
#   python geointel.py Turkey
#   python geointel.py "South Korea"

if __name__ == "__main__":
    # Get country from command line argument, or ask for it
    if len(sys.argv) > 1:
        country = " ".join(sys.argv[1:])
    else:
        country = input("🌍 Enter a country name: ")

    # Generate and print the briefing
    briefing = generate_briefing(country)
    print(briefing)

    # Also save to a file so you have it
    filename = f"briefing_{country.lower().replace(' ', '_')}.md"
    with open(filename, "w") as f:
        f.write(f"# GeoIntel AI Briefing: {country}\n\n")
        f.write(briefing)

    print(f"\n✅ Briefing saved to: {filename}")
