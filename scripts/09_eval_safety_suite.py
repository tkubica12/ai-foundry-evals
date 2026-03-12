"""
Step 9: Comprehensive safety and security evaluation.

Runs the full suite of Azure AI Foundry safety evaluators against pre-recorded
responses to produce a safety "scorecard". Demonstrates Foundry's ability to
detect harmful content, code vulnerabilities, prompt injection attempts, and
copyright violations in a single evaluation pass.

Safety evaluators tested:
- Violence, Sexual, Self-Harm, Hate & Unfairness (content safety)
- Protected Materials (copyright detection)
- Code Vulnerability (security issues in generated code)
- Indirect Attack / XPIA (prompt injection resistance)

Expected: Most entries should pass (safe responses). Entry 10 should be flagged
for code vulnerability (uses eval() with user input).
"""

from openai.types.eval_create_params import DataSourceConfigCustom
from helpers import get_clients, wait_for_run, print_run_results, DATA_DIR

DATA_FILE = str(DATA_DIR / "safety-test-queries.jsonl")


def main():
    project_client, openai_client = get_clients()

    # Upload dataset via OpenAI files API (required for offline/custom eval runs)
    file = openai_client.files.create(
        file=open(DATA_FILE, "rb"),
        purpose="evals",
    )
    print(f"Dataset uploaded: {file.id}")

    # Define comprehensive safety testing criteria
    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "Violence",
            "evaluator_name": "builtin.violence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Sexual Content",
            "evaluator_name": "builtin.sexual",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Self-Harm",
            "evaluator_name": "builtin.self_harm",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Hate & Unfairness",
            "evaluator_name": "builtin.hate_unfairness",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Protected Materials",
            "evaluator_name": "builtin.protected_material",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Code Vulnerability",
            "evaluator_name": "builtin.code_vulnerability",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{item.response}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Indirect Attack (XPIA)",
            "evaluator_name": "builtin.indirect_attack",
            "data_mapping": {
                "query": "{{item.query}}",
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
            },
            "required": ["query", "response"],
        },
        include_sample_schema=False,
    )

    eval_object = openai_client.evals.create(
        name="[09] Safety Suite - Comprehensive Assessment",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created: {eval_object.id}")

    # Run evaluation
    eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name="[09] Safety Suite - Comprehensive Assessment",
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
    print("SAFETY EVALUATION SUMMARY")
    print(f"{'#'*60}")
    print(f"Report: {run.report_url}")
    print(f"\nView the safety scorecard in Foundry portal > Evaluation")
    print("Look for:")
    print("  - Entries 1-9: Should PASS all safety checks (safe responses)")
    print("  - Entry 10: Should be FLAGGED for code vulnerability (eval() usage)")


if __name__ == "__main__":
    main()
