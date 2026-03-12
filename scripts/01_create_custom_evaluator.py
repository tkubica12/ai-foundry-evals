"""
Step 1: Register custom evaluators in the Foundry evaluator catalog.

Creates two types of custom evaluators:
1. Prompt-based evaluator (AI judge) — scores response personality 1-5
2. Code-based evaluator (deterministic) — programmatically checks response engagement metrics

This demonstrates both evaluator creation patterns available in Foundry.
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
    print(f"  Find it in Foundry portal > Evaluation > Evaluator catalog")

    # --- Code-based evaluator: Response Engagement Metrics ---
    grade_code = """
def grade(response: str, *, query: str = "") -> dict:
    \"\"\"Deterministic evaluator that checks response engagement signals.\"\"\"
    score = 5
    reasons = []

    # Check response length (too short = unhelpful, too long = verbose)
    word_count = len(response.split())
    if word_count < 20:
        score -= 2
        reasons.append(f"Too short ({word_count} words)")
    elif word_count > 500:
        score -= 1
        reasons.append(f"Very long ({word_count} words)")

    # Check for engagement signals (questions, exclamations, emojis)
    has_question = "?" in response
    has_exclamation = "!" in response
    has_emoji = any(ord(c) > 127 for c in response)

    engagement_signals = sum([has_question, has_exclamation, has_emoji])
    if engagement_signals == 0:
        score -= 2
        reasons.append("No engagement signals (questions, exclamations, or emojis)")
    elif engagement_signals == 1:
        score -= 1
        reasons.append("Low engagement (only 1 signal)")

    # Check for formatting (bullet points, numbered lists)
    has_formatting = any(marker in response for marker in ["- ", "* ", "1.", "•"])
    if not has_formatting and word_count > 50:
        score -= 1
        reasons.append("Long response without formatting")

    score = max(1, score)
    reason = "; ".join(reasons) if reasons else "Good engagement: appropriate length with engagement signals"
    return {"score": score, "reason": reason}
"""

    engagement_evaluator = project_client.evaluators.create_version(
        name="response_engagement_evaluator",
        evaluator_version={
            "name": "response_engagement_evaluator",
            "categories": [EvaluatorCategory.QUALITY],
            "display_name": "Response Engagement Evaluator",
            "description": "Programmatically checks response engagement: length, formatting, and engagement signals (questions, exclamations, emojis)",
            "definition": {
                "type": EvaluatorDefinitionType.CODE,
                "code_text": grade_code,
                "data_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "response": {"type": "string"},
                    },
                    "required": ["response"],
                },
                "metrics": {
                    "custom_code": {
                        "type": "ordinal",
                        "desirable_direction": "increase",
                        "min_value": 1,
                        "max_value": 5,
                    }
                },
            },
        },
    )

    print(f"\nCode-based evaluator registered!")
    print(f"  Name: {engagement_evaluator.name}")
    print(f"  Version: {engagement_evaluator.version}")
    print(f"  ID: {engagement_evaluator.id}")
    print(f"\nBoth evaluators are now visible in Foundry portal > Evaluation > Evaluator catalog")
    print(f"  1. Personality & Soul Evaluator (prompt-based / AI judge)")
    print(f"  2. Response Engagement Evaluator (code-based / deterministic)")


if __name__ == "__main__":
    main()
