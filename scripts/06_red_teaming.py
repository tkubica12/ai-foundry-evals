"""
Step 6: Red-team the teen-friendly agent.

Uses Azure AI Foundry's automated red-teaming to probe the agent for safety
vulnerabilities. The workflow:
  1. Create a red team (OpenAI evals API) with safety evaluators
  2. Create an evaluation taxonomy for the target agent + risk categories
  3. Run a red-team evaluation with multiple attack strategies
  4. Poll for completion and print ASR results
"""

import time
from azure.ai.projects.models import (
    AzureAIAgentTarget,
    AgentTaxonomyInput,
    EvaluationTaxonomy,
    RiskCategory,
)
from helpers import get_clients, wait_for_run, print_run_results, MODEL_DEPLOYMENT

AGENT_NAME = "teen-friendly-assistant"

# Risk categories most relevant for a teen-facing assistant
RISK_CATEGORIES = [
    RiskCategory.VIOLENCE,
    RiskCategory.HATE_UNFAIRNESS,
    RiskCategory.PROHIBITED_ACTIONS,
    RiskCategory.SENSITIVE_DATA_LEAKAGE,
]

APPLICATION_SCENARIO = (
    "A fun, friendly AI assistant called Vibe designed specifically for "
    "teenagers. It uses casual language, emojis, and pop-culture references. "
    "It must always be age-appropriate and refuse dangerous or inappropriate requests."
)


def main():
    project_client, openai_client = get_clients()

    # Get latest agent version
    versions = list(project_client.agents.list_versions(agent_name=AGENT_NAME))
    latest = max(versions, key=lambda a: int(a.version))
    agent_version = str(latest.version)
    print(f"Target agent: {AGENT_NAME} v{agent_version}")

    # ----- Step 1: Create red team (eval group) with safety evaluators -----
    red_team = openai_client.evals.create(
        name=f"Red Team – {AGENT_NAME}",
        data_source_config={"type": "azure_ai_source", "scenario": "red_team"},
        testing_criteria=[
            {
                "type": "azure_ai_evaluator",
                "name": "Violence",
                "evaluator_name": "builtin.violence",
                "evaluator_version": "1",
            },
            {
                "type": "azure_ai_evaluator",
                "name": "Prohibited Actions",
                "evaluator_name": "builtin.prohibited_actions",
                "evaluator_version": "1",
            },
            {
                "type": "azure_ai_evaluator",
                "name": "Task Adherence",
                "evaluator_name": "builtin.task_adherence",
                "evaluator_version": "1",
                "initialization_parameters": {"deployment_name": MODEL_DEPLOYMENT},
            },
            {
                "type": "azure_ai_evaluator",
                "name": "Sensitive Data Leakage",
                "evaluator_name": "builtin.sensitive_data_leakage",
                "evaluator_version": "1",
            },
        ],
    )
    print(f"\n1. Red team eval created: {red_team.id}")

    # ----- Step 2: Create evaluation taxonomy for prohibited actions -----
    # Note: Taxonomy currently only supports ProhibitedActions risk category.
    # Other safety categories (violence, etc.) are evaluated by the safety
    # evaluators attached to the red team eval, not through the taxonomy.
    target = AzureAIAgentTarget(name=AGENT_NAME, version=agent_version)

    taxonomy = project_client.evaluation_taxonomies.create(
        name=AGENT_NAME,
        body=EvaluationTaxonomy(
            description=f"Red teaming taxonomy for {AGENT_NAME}",
            taxonomy_input=AgentTaxonomyInput(
                risk_categories=[RiskCategory.PROHIBITED_ACTIONS],
                target=target,
            ),
        ),
    )
    taxonomy_file_id = taxonomy.id
    print(f"2. Taxonomy created: {taxonomy_file_id}")

    # ----- Step 3: Create a red-team run with attack strategies -----
    attack_strategies = ["Flip", "Base64", "Jailbreak"]
    print(f"\n3. Starting red-team run...")
    print(f"   Attack strategies: {attack_strategies}")
    print(f"   Turns per conversation: 3")

    eval_run = openai_client.evals.runs.create(
        eval_id=red_team.id,
        name=f"Red Team Run – {AGENT_NAME}",
        data_source={
            "type": "azure_ai_red_team",
            "item_generation_params": {
                "type": "red_team_taxonomy",
                "attack_strategies": attack_strategies,
                "num_turns": 3,
                "source": {"type": "file_id", "id": taxonomy_file_id},
            },
            "target": target.as_dict(),
        },
    )
    print(f"   Run started: {eval_run.id} (status: {eval_run.status})")

    # ----- Step 4: Poll for completion (red teaming takes ~10-30 min) -----
    print("\nWaiting for red-team run to complete (this takes ~10-30 min)...")
    final = wait_for_run(openai_client, red_team.id, eval_run.id, poll_interval=30)

    # ----- Step 5: Print results -----
    print_run_results(openai_client, red_team.id, final)

    print(f"\nView full results in Foundry portal > Evaluation")
    print(f"Red team eval ID: {red_team.id}")
    print(f"Run ID: {final.id}")


if __name__ == "__main__":
    main()
