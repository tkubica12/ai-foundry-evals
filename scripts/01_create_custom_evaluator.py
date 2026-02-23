"""
Step 1: Register custom personality evaluator in the Foundry evaluator catalog.

This creates a prompt-based evaluator that assesses whether an AI response has
a fun, friendly, teenager-oriented personality (warm tone, casual language,
engaging style) vs. a boring/corporate/professional tone.

Scoring: 1-5 ordinal scale (5 = very fun & teen-friendly)
"""

from azure.ai.projects.models import EvaluatorCategory, EvaluatorDefinitionType
from helpers import get_clients, MODEL_DEPLOYMENT

PERSONALITY_PROMPT = """You are evaluating whether an AI assistant's response has a fun, friendly, \
teenager-oriented personality.

Rate the personality/soul of the response on a scale of 1 to 5:

1 - Very boring, corporate, or robotic. Uses formal/professional language with no personality.
2 - Mostly dry and impersonal. Might have slight warmth but reads like a textbook.
3 - Neutral. Neither particularly fun nor boring. Average conversational tone.
4 - Friendly and engaging. Uses casual language, shows some personality and warmth. \
Feels approachable for a teenager.
5 - Extremely fun, warm, and teenager-friendly! Uses casual/trendy language, \
emojis or exclamations, humor, encouragement, and feels like talking to a cool older friend. \
Very engaging and relatable for teens.

Consider these factors:
- Tone: Is it warm, enthusiastic, and encouraging?
- Language: Does it use casual, age-appropriate language (not overly formal)?
- Engagement: Does it hook the reader and keep things interesting?
- Relatability: Would a teenager enjoy reading this response?
- Personality: Does the response have a distinct, memorable voice?

Query: {{query}}

Response: {{response}}

Output Format (JSON):
{
  "result": <integer from 1 to 5>,
  "reason": "<brief explanation for the score>"
}
"""

def main():
    project_client, _ = get_clients()

    evaluator = project_client.evaluators.create_version(
        name="personality_soul_evaluator",
        evaluator_version={
            "name": "personality_soul_evaluator",
            "categories": [EvaluatorCategory.QUALITY],
            "display_name": "Personality & Soul Evaluator",
            "description": "Evaluates whether responses have a fun, friendly, teen-oriented personality vs boring/professional tone",
            "definition": {
                "type": EvaluatorDefinitionType.PROMPT,
                "prompt_text": PERSONALITY_PROMPT,
                "init_parameters": {
                    "type": "object",
                    "properties": {
                        "deployment_name": {"type": "string"},
                        "threshold": {"type": "number"},
                    },
                    "required": ["deployment_name", "threshold"],
                },
                "data_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "response": {"type": "string"},
                    },
                    "required": ["query", "response"],
                },
                "metrics": {
                    "custom_prompt": {
                        "type": "ordinal",
                        "desirable_direction": "increase",
                        "min_value": 1,
                        "max_value": 5,
                    }
                },
            },
        },
    )

    print(f"Custom evaluator registered!")
    print(f"  Name: {evaluator.name}")
    print(f"  Version: {evaluator.version}")
    print(f"  ID: {evaluator.id}")
    print(f"\nYou can now see it in Foundry portal > Evaluation > Evaluator catalog")


if __name__ == "__main__":
    main()
