"""
Step 10: Online RAG evaluation — live agent with document retrieval.

Creates a RAG agent with file search over the TechVibe Solutions employee handbook,
then evaluates it live with Foundry's RAG and quality evaluators. Unlike script 07
(offline evaluation of pre-recorded data), this script tests a real agent that
retrieves documents and generates answers in real-time.

Foundry's Groundedness evaluator automatically extracts context from the agent's
file search tool calls — no manual context mapping needed.

Evaluators: Groundedness, Relevance, Response Completeness, Coherence, Fluency
"""

import time as _time

from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition
from openai.types.eval_create_params import DataSourceConfigCustom
from helpers import get_clients, wait_for_run, print_run_results, MODEL_DEPLOYMENT, DATA_DIR

AGENT_NAME = "rag-handbook-assistant"
DATA_FILE = str(DATA_DIR / "rag-agent-test-queries.jsonl")
HANDBOOK_FILE = str(DATA_DIR / "techvibe-handbook.md")

RAG_AGENT_INSTRUCTIONS = """\
You are a helpful HR assistant for TechVibe Solutions. Answer employee questions \
using the company handbook and policy documents available through file search.

Rules:
- Always search the uploaded documents before answering
- Base your answers strictly on the information found in the documents
- If the documents don't contain the answer, say so clearly
- Cite specific policy sections when possible
- Keep answers concise and accurate
"""


def build_testing_criteria(model_deployment):
    """Build testing criteria with RAG + quality evaluators."""
    return [
        {
            "type": "azure_ai_evaluator",
            "name": "Groundedness",
            "evaluator_name": "builtin.groundedness",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Relevance",
            "evaluator_name": "builtin.relevance",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Response Completeness",
            "evaluator_name": "builtin.response_completeness",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "ground_truth": "{{item.ground_truth}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Coherence",
            "evaluator_name": "builtin.coherence",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Fluency",
            "evaluator_name": "builtin.fluency",
            "initialization_parameters": {"deployment_name": model_deployment},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
    ]


def main():
    project_client, openai_client = get_clients()

    # --- Step 1: Create vector store and upload handbook ---
    print(f"{'='*60}")
    print("STEP 1: Creating vector store and uploading handbook")
    print(f"{'='*60}")

    vector_store = openai_client.vector_stores.create(name="TechVibeHandbookStore")
    with open(HANDBOOK_FILE, "rb") as f:
        openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=f,
        )
    print(f"Vector store created: {vector_store.id}")

    # --- Step 2: Create RAG agent with file search ---
    print(f"\n{'='*60}")
    print("STEP 2: Creating RAG agent with file search")
    print(f"{'='*60}")

    file_search = FileSearchTool(vector_store_ids=[vector_store.id])

    agent = project_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL_DEPLOYMENT,
            instructions=RAG_AGENT_INSTRUCTIONS,
            tools=[file_search],
        ),
        description="RAG agent with file search over TechVibe employee handbook.",
    )
    print(f"Agent created: {agent.name} (version {agent.version})")

    # --- Step 3: Upload test dataset ---
    print(f"\n{'='*60}")
    print("STEP 3: Uploading test dataset")
    print(f"{'='*60}")

    version = str(int(_time.time()))
    dataset = project_client.datasets.upload_file(
        name="10-rag-agent-queries",
        version=version,
        file_path=DATA_FILE,
    )
    print(f"Dataset uploaded: {dataset.id}")

    # --- Step 4: Create and run evaluation ---
    print(f"\n{'='*60}")
    print("STEP 4: Running RAG evaluation")
    print(f"{'='*60}")

    testing_criteria = build_testing_criteria(MODEL_DEPLOYMENT)

    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "ground_truth": {"type": "string"},
            },
            "required": ["query", "ground_truth"],
        },
        include_sample_schema=True,
    )

    eval_name = f"[10] RAG Agent - {AGENT_NAME}"
    eval_object = openai_client.evals.create(
        name=eval_name,
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created: {eval_object.id} ({eval_name})")

    data_source = {
        "type": "azure_ai_target_completions",
        "source": {"type": "file_id", "id": dataset.id},
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
            "name": AGENT_NAME,
            "version": str(agent.version),
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

    # --- Step 5: Summary ---
    print(f"\n{'#'*60}")
    print("RAG EVALUATION SUMMARY")
    print(f"{'#'*60}")
    print(f"Agent: {AGENT_NAME} (version {agent.version})")
    print(f"Vector store: {vector_store.id}")
    print(f"Report: {run.report_url}")
    print("\nEvaluators used:")
    print("  - Groundedness (RAG — context extracted from file search calls)")
    print("  - Relevance")
    print("  - Response Completeness (compared against ground truth)")
    print("  - Coherence")
    print("  - Fluency")
    print("\nView detailed results in Foundry portal > Evaluation.")


if __name__ == "__main__":
    main()
