"""
Step 5: Set up continuous evaluation for the Teen_Friendly_Assistant agent.

Creates a continuous evaluation rule that automatically evaluates agent responses
in production. Every time the agent completes a response, the rule triggers
evaluators on a sample of those responses.
"""

from azure.ai.projects.models import (
    EvaluationRule,
    ContinuousEvaluationRuleAction,
    EvaluationRuleFilter,
    EvaluationRuleEventType,
)
from helpers import get_clients, MODEL_DEPLOYMENT

AGENT_NAME = "teen-friendly-assistant"


def main():
    project_client, openai_client = get_clients()

    # Define continuous eval data source and testing criteria
    data_source_config = {"type": "azure_ai_source", "scenario": "responses"}

    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "violence_detection",
            "evaluator_name": "builtin.violence",
        },
        {
            "type": "azure_ai_evaluator",
            "name": "coherence",
            "evaluator_name": "builtin.coherence",
            "initialization_parameters": {"deployment_name": MODEL_DEPLOYMENT},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "personality_check",
            "evaluator_name": "personality_soul_evaluator",
            "initialization_parameters": {
                "deployment_name": MODEL_DEPLOYMENT,
                "threshold": 3,
            },
        },
    ]

    # Create the evaluation definition
    eval_object = openai_client.evals.create(
        name="[05] Continuous Monitoring - teen-friendly-assistant",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created: {eval_object.id} ({eval_object.name})")

    # Create the continuous evaluation rule
    continuous_eval_rule = project_client.evaluation_rules.create_or_update(
        id="teen-assistant-continuous-eval",
        evaluation_rule=EvaluationRule(
            display_name="[05] Continuous Quality Monitor",
            description="Continuously evaluates Teen_Friendly_Assistant responses for violence, coherence, and personality",
            action=ContinuousEvaluationRuleAction(
                eval_id=eval_object.id,
                max_hourly_runs=50,
            ),
            event_type=EvaluationRuleEventType.RESPONSE_COMPLETED,
            filter=EvaluationRuleFilter(agent_name=AGENT_NAME),
            enabled=True,
        ),
    )

    print(f"\nContinuous Evaluation Rule created!")
    print(f"  ID: {continuous_eval_rule.id}")
    print(f"  Name: {continuous_eval_rule.display_name}")
    print(f"  Agent: {AGENT_NAME}")
    print(f"\nView in Foundry portal > Monitoring > Agent Monitoring Dashboard")
    print("The rule will automatically evaluate agent responses in production.")


if __name__ == "__main__":
    main()
