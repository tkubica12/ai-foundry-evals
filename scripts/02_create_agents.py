"""
Step 2: Create two Foundry agents for comparison.

Agent A ("generic-assistant"): Plain prompt, no personality.
Agent B ("teen-friendly-assistant"): Rich soul definition - fun, friendly, teenager-oriented.

Both use the same model and have access to Bing web search for grounding,
so the only difference is the system prompt / soul.
"""

from azure.ai.projects.models import (
    BingGroundingAgentTool,
    BingGroundingSearchConfiguration,
    BingGroundingSearchToolParameters,
    PromptAgentDefinition,
)
from helpers import get_clients, MODEL_DEPLOYMENT

BING_CONNECTION_ID = "groundingbingtokubica"

AGENT_A_NAME = "generic-assistant"
AGENT_A_INSTRUCTIONS = "You are a helpful assistant. Answer user questions accurately and concisely."

AGENT_B_NAME = "teen-friendly-assistant"
AGENT_B_INSTRUCTIONS = """\
You are Vibe, a super cool and friendly AI buddy designed specifically for teenagers! 🎉

YOUR PERSONALITY & SOUL:
- You're like that awesome older friend who knows a lot but never talks down to anyone
- You use casual, fun language with occasional emojis (but don't overdo it!)
- You're enthusiastic and encouraging - you genuinely get excited about helping
- You explain complex things using relatable examples from pop culture, gaming, social media, and everyday teen life
- You're warm, supportive, and always positive (especially about school stress, social pressure, etc.)
- You use humor naturally - throw in jokes, fun analogies, and playful language
- You say things like "no cap", "let's gooo", "that's fire", "fr fr" occasionally but naturally
- You never lecture or sound like a textbook or a parent
- You keep responses engaging with bullet points, short paragraphs, and fun formatting
- If someone seems stressed or down, you're empathetic first, helpful second

IMPORTANT RULES:
- Always be age-appropriate and responsible
- If asked about dangerous topics, redirect kindly without being preachy
- Make learning feel like discovering something cool, not homework
- Keep the energy up! Every response should feel like it was fun to write
"""


def main():
    project_client, _ = get_clients()

    # Bing grounding tool – gives both agents access to web search
    bing_tool = BingGroundingAgentTool(
        bing_grounding=BingGroundingSearchToolParameters(
            search_configurations=[
                BingGroundingSearchConfiguration(
                    project_connection_id=BING_CONNECTION_ID,
                )
            ]
        )
    )

    # --- Agent A: Generic (no personality) ---
    agent_a = project_client.agents.create_version(
        agent_name=AGENT_A_NAME,
        definition=PromptAgentDefinition(
            model=MODEL_DEPLOYMENT,
            instructions=AGENT_A_INSTRUCTIONS,
            tools=[bing_tool],
        ),
        description="Plain assistant with no personality definition. Has web search.",
    )
    print(f"Agent A created: {agent_a.name} (version {agent_a.version})")

    # --- Agent B: Teen-friendly with soul ---
    agent_b = project_client.agents.create_version(
        agent_name=AGENT_B_NAME,
        definition=PromptAgentDefinition(
            model=MODEL_DEPLOYMENT,
            instructions=AGENT_B_INSTRUCTIONS,
            tools=[bing_tool],
        ),
        description="Fun, friendly assistant with a teen-oriented personality/soul. Has web search.",
    )
    print(f"Agent B created: {agent_b.name} (version {agent_b.version})")

    print(f"\nBoth agents are now visible in Foundry portal > Agents")
    print(f"Agent A (generic): {AGENT_A_NAME}:{agent_a.version}")
    print(f"Agent B (with soul): {AGENT_B_NAME}:{agent_b.version}")


if __name__ == "__main__":
    main()
