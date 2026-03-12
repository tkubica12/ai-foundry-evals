"""
Step 7: Offline RAG evaluation — pre-recorded responses.

Evaluates pre-recorded RAG responses for groundedness, relevance, and completeness.
The dataset contains responses from a company knowledge base Q&A system — some are
well-grounded, while others contain hallucinations or miss critical information.
This offline approach is useful for regression testing without running a live agent.

For live agent RAG evaluation with actual document retrieval, see script 10.

Foundry's RAG evaluators detect:
- Hallucinated content not supported by the retrieved context (Groundedness)
- Responses that don't address the query (Relevance)
- Incomplete responses missing critical information (Response Completeness)

Expected: Entries 7-8 should fail Groundedness (hallucinated details), entry 9 should
fail Response Completeness (missing critical info), and entry 10 should show low
Relevance (irrelevant context retrieved).
"""

from openai.types.eval_create_params import DataSourceConfigCustom
from helpers import get_clients, wait_for_run, print_run_results, MODEL_DEPLOYMENT, DATA_DIR

DATA_FILE = str(DATA_DIR / "rag-test-queries.jsonl")


def main():
    project_client, openai_client = get_clients()

    # Upload dataset via OpenAI files API (required for offline/custom eval runs)
    file = openai_client.files.create(
        file=open(DATA_FILE, "rb"),
        purpose="evals",
    )
    print(f"Dataset uploaded: {file.id}")

    # Define testing criteria
    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "Groundedness",
            "evaluator_name": "builtin.groundedness",
            "initialization_parameters": {"deployment_name": MODEL_DEPLOYMENT},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
                "context": "{{item.context}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Relevance",
            "evaluator_name": "builtin.relevance",
            "initialization_parameters": {"deployment_name": MODEL_DEPLOYMENT},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Response Completeness",
            "evaluator_name": "builtin.response_completeness",
            "initialization_parameters": {"deployment_name": MODEL_DEPLOYMENT},
            "data_mapping": {
                "ground_truth": "{{item.ground_truth}}",
                "response": "{{item.response}}",
            },
        },
    ]

    # Create evaluation
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "response": {"type": "string"},
                "context": {"type": "string"},
                "ground_truth": {"type": "string"},
            },
            "required": ["query", "response", "context", "ground_truth"],
        },
        include_sample_schema=False,
    )

    eval_object = openai_client.evals.create(
        name="[07] RAG Offline - Groundedness & Completeness",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created: {eval_object.id}")

    # Run evaluation (no target — evaluating pre-recorded data)
    eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name="[07] RAG Offline - Groundedness & Completeness",
        data_source={
            "type": "jsonl",
            "source": {"type": "file_id", "id": file.id},
        },
    )
    print(f"Run started: {eval_run.id}")

    run = wait_for_run(openai_client, eval_object.id, eval_run.id)
    print_run_results(openai_client, eval_object.id, run)

    # Summary
    print(f"\n{'#'*60}")
    print("RAG EVALUATION SUMMARY")
    print(f"{'#'*60}")
    print(f"Report: {run.report_url}")
    print(f"\nView detailed results in Foundry portal > Evaluation")
    print("Look for:")
    print("  - Entries 7-8: Should FAIL Groundedness (hallucinated details)")
    print("  - Entry 9: Should FAIL Response Completeness (missing critical info)")
    print("  - Entry 10: Should show low Relevance (irrelevant context)")


if __name__ == "__main__":
    main()
