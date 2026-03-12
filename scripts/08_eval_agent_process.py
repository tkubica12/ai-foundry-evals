"""
Step 8: Evaluate agent reasoning process — intent, tool usage, and task completion.

Uses Foundry's agentic process evaluators to assess HOW agents reason and act,
not just what they output. Tests whether agents correctly identify user intent,
use tools effectively (Bing web search), and fully complete tasks.

Expected: Both agents should score well on intent resolution, but the teen-friendly
agent may show different tool usage patterns due to its personality-driven approach.
"""

from openai.types.eval_create_params import DataSourceConfigCustom
from helpers import get_clients, wait_for_run, print_run_results, MODEL_DEPLOYMENT, DATA_DIR

AGENT_A_NAME = "generic-assistant"
AGENT_B_NAME = "teen-friendly-assistant"
DATA_FILE = str(DATA_DIR / "agent-test-queries.jsonl")


def build_testing_criteria(model_deployment):
    """Build testing criteria with agentic process evaluators."""
    return [
        {
            "type": "azure_ai_evaluator",
            "name": "Intent Resolution",
            "evaluator_name": "builtin.intent_resolution",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Tool Call Accuracy",
            "evaluator_name": "builtin.tool_call_accuracy",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
                "tool_definitions": "{{sample.tool_definitions}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Task Completion",
            "evaluator_name": "builtin.task_completion",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        },
    ]


def run_agent_eval(project_client, openai_client, agent_name, agent_version, dataset_id, eval_name):
    """Create an evaluation and run it against a specific agent."""
    testing_criteria = build_testing_criteria(MODEL_DEPLOYMENT)

    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
        include_sample_schema=True,
    )

    eval_object = openai_client.evals.create(
        name=eval_name,
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created: {eval_object.id} ({eval_name})")

    data_source = {
        "type": "azure_ai_target_completions",
        "source": {"type": "file_id", "id": dataset_id},
        "input_messages": {
            "type": "template",
            "template": [
                {
                    "type": "message",
                    "role": "user",
                    "content": {"type": "input_text", "text": "{{item.query}}"},
                }
            ],
        },
        "target": {
            "type": "azure_ai_agent",
            "name": agent_name,
            "version": str(agent_version),
        },
    }

    eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name=eval_name,
        data_source=data_source,
    )
    print(f"Run started: {eval_run.id}")

    run = wait_for_run(openai_client, eval_object.id, eval_run.id)
    print_run_results(openai_client, eval_object.id, run)
    return run


def main():
    project_client, openai_client = get_clients()

    # Upload dataset
    import time as _time
    version = str(int(_time.time()))
    dataset = project_client.datasets.upload_file(
        name="08-agent-process-queries",
        version=version,
        file_path=DATA_FILE,
    )
    print(f"Dataset uploaded: {dataset.id}")

    # Get agent versions
    agents = {AGENT_A_NAME: None, AGENT_B_NAME: None}
    for name in agents:
        versions = list(project_client.agents.list_versions(agent_name=name))
        latest = max(versions, key=lambda a: int(a.version))
        agents[name] = latest.version
        print(f"Agent '{name}' latest version: {latest.version}")

    # Run evaluation for Agent A (generic)
    print(f"\n{'='*60}")
    print(f"EVALUATING AGENT A: {AGENT_A_NAME} (no personality)")
    print(f"{'='*60}")
    run_a = run_agent_eval(
        project_client, openai_client,
        AGENT_A_NAME, agents[AGENT_A_NAME], dataset.id,
        f"[08] Agent Process - {AGENT_A_NAME}",
    )

    # Run evaluation for Agent B (with soul)
    print(f"\n{'='*60}")
    print(f"EVALUATING AGENT B: {AGENT_B_NAME} (with personality)")
    print(f"{'='*60}")
    run_b = run_agent_eval(
        project_client, openai_client,
        AGENT_B_NAME, agents[AGENT_B_NAME], dataset.id,
        f"[08] Agent Process - {AGENT_B_NAME}",
    )

    # Summary
    print(f"\n{'#'*60}")
    print("COMPARISON SUMMARY")
    print(f"{'#'*60}")
    print(f"Agent A ({AGENT_A_NAME}): {run_a.report_url}")
    print(f"Agent B ({AGENT_B_NAME}): {run_b.report_url}")
    print("\nCompare these in Foundry portal > Evaluation to see the difference!")
    print("Expected: Both agents should resolve intent well; tool usage patterns")
    print("may differ due to personality-driven approach in the teen-friendly agent.")


if __name__ == "__main__":
    main()
