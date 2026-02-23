"""
Step 4: Compare models - gpt-4.1-nano vs gpt-5.2 on hard computation tasks.

Sends challenging computation/reasoning queries (with known ground-truth answers)
to both models and evaluates with Coherence, Fluency, Relevance, a custom
Reasoning Depth evaluator, and a custom Correctness evaluator that compares
against known answers. The Correctness evaluator should produce notably lower
scores for the smaller model.
"""

from azure.ai.projects.models import EvaluatorCategory, EvaluatorDefinitionType
from openai.types.eval_create_params import DataSourceConfigCustom
from helpers import get_clients, wait_for_run, print_run_results, MODEL_DEPLOYMENT, MODEL_SMALL, MODEL_LARGE, DATA_DIR

DATA_FILE = str(DATA_DIR / "model-test-queries.jsonl")

REASONING_DEPTH_PROMPT = """You are an expert evaluator assessing the depth and accuracy of reasoning \
in a response to a complex academic question.

Rate the reasoning depth on a scale of 1 to 5:

1 - Superficial or wrong. Gives a vague overview, misses key concepts, contains factual errors, \
or fails to engage with the complexity of the question.
2 - Shallow. Touches on some relevant points but lacks depth. Missing important nuances, \
key details, or logical steps.
3 - Adequate. Covers the main points correctly but without exceptional depth. \
A competent but not impressive response.
4 - Deep and accurate. Demonstrates strong understanding, covers nuances, provides \
specific examples, and engages with the complexity of the question well.
5 - Exceptional. Expert-level response with comprehensive coverage, precise terminology, \
specific examples, logical rigor, and original insights. Could serve as educational material.

Consider these factors:
- Accuracy: Are the facts and concepts correct?
- Depth: Does it go beyond surface-level explanation?
- Specificity: Does it use concrete examples, names, equations, or references?
- Logical structure: Is the reasoning well-organized and step-by-step?
- Completeness: Does it address all parts of the question?

Query: {{query}}

Response: {{response}}

Output Format (JSON):
{
  "result": <integer from 1 to 5>,
  "reason": "<brief explanation for the score>"
}
"""

CORRECTNESS_PROMPT = """You are a strict grading assistant. You are given a question, \
a reference answer (ground truth) with the correct values, and a student's response. \
Your job is to check whether the student's response contains the CORRECT final numerical \
answers and key results from the reference answer.

GRADING RULES (be very strict):
- Focus ONLY on whether the final numerical values and key results match the ground truth.
- Ignore differences in formatting, explanation style, or intermediate steps.
- If the response gets the final answer wrong (even by a small amount), score LOW.
- If the response gets most final answers right but misses one key result, score 3.
- If the response produces all correct final values, score 5.
- If the response is completely off or doesn't attempt the computation, score 1.

Scale:
1 - Wrong answer. Key numerical results are incorrect or missing entirely.
2 - Mostly wrong. Some parts attempted but final answers have significant errors.
3 - Partially correct. Some final values are right but others are wrong or missing.
4 - Mostly correct. All main final values are correct with minor issues in secondary results.
5 - Fully correct. All key numerical results match the ground truth.

Question: {{query}}

Reference Answer (Ground Truth): {{ground_truth}}

Student Response: {{response}}

Output Format (JSON):
{
  "result": <integer from 1 to 5>,
  "reason": "<brief explanation identifying which values are correct or incorrect>"
}
"""


def run_model_eval(project_client, openai_client, model_name, dataset_id, eval_name):
    """Create an evaluation and run against a model target."""

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

    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "Coherence",
            "evaluator_name": "builtin.coherence",
            "initialization_parameters": {"deployment_name": MODEL_DEPLOYMENT},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Fluency",
            "evaluator_name": "builtin.fluency",
            "initialization_parameters": {"deployment_name": MODEL_DEPLOYMENT},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Relevance",
            "evaluator_name": "builtin.relevance",
            "initialization_parameters": {"deployment_name": MODEL_DEPLOYMENT},
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Reasoning Depth",
            "evaluator_name": "reasoning_depth_evaluator",
            "initialization_parameters": {
                "deployment_name": MODEL_DEPLOYMENT,
                "threshold": 3,
            },
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Correctness",
            "evaluator_name": "correctness_evaluator",
            "initialization_parameters": {
                "deployment_name": MODEL_DEPLOYMENT,
                "threshold": 3,
            },
            "data_mapping": {
                "query": "{{item.query}}",
                "ground_truth": "{{item.ground_truth}}",
                "response": "{{sample.output_text}}",
            },
        },
    ]

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
            "type": "azure_ai_model",
            "model": model_name,
            "sampling_params": {
                "max_completion_tokens": 4096,
                "top_p": 1.0,
            },
        },
    }

    eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"{eval_name} - Run",
        data_source=data_source,
    )
    print(f"Run started: {eval_run.id}")

    run = wait_for_run(openai_client, eval_object.id, eval_run.id)
    print_run_results(openai_client, eval_object.id, run)
    return run


def main():
    project_client, openai_client = get_clients()

    # Register reasoning depth evaluator (idempotent - will create new version if exists)
    try:
        project_client.evaluators.create_version(
            name="reasoning_depth_evaluator",
            evaluator_version={
                "name": "reasoning_depth_evaluator",
                "categories": [EvaluatorCategory.QUALITY],
                "display_name": "Reasoning Depth Evaluator",
                "description": "Evaluates the depth and accuracy of reasoning in responses to complex academic questions",
                "definition": {
                    "type": EvaluatorDefinitionType.PROMPT,
                    "prompt_text": REASONING_DEPTH_PROMPT,
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
        print("Reasoning Depth evaluator registered!")
    except Exception as e:
        print(f"Reasoning Depth evaluator already exists or error: {e}")

    # Register correctness evaluator (checks against ground truth)
    try:
        project_client.evaluators.create_version(
            name="correctness_evaluator",
            evaluator_version={
                "name": "correctness_evaluator",
                "categories": [EvaluatorCategory.QUALITY],
                "display_name": "Correctness Evaluator",
                "description": "Checks whether the response contains correct numerical answers by comparing against ground truth",
                "definition": {
                    "type": EvaluatorDefinitionType.PROMPT,
                    "prompt_text": CORRECTNESS_PROMPT,
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
                            "ground_truth": {"type": "string"},
                            "response": {"type": "string"},
                        },
                        "required": ["query", "ground_truth", "response"],
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
        print("Correctness evaluator registered!")
    except Exception as e:
        print(f"Correctness evaluator already exists or error: {e}")

    # Upload dataset (use unique version to avoid conflicts)
    import time
    version = str(int(time.time()))
    dataset = project_client.datasets.upload_file(
        name="model-reasoning-test-queries",
        version=version,
        file_path=DATA_FILE,
    )
    print(f"Dataset uploaded: {dataset.id}")

    # Evaluate small model
    print(f"\n{'='*60}")
    print(f"EVALUATING MODEL: {MODEL_SMALL} (small)")
    print(f"{'='*60}")
    run_small = run_model_eval(
        project_client, openai_client,
        MODEL_SMALL, dataset.id,
        f"Model Eval - {MODEL_SMALL}",
    )

    # Evaluate large model
    print(f"\n{'='*60}")
    print(f"EVALUATING MODEL: {MODEL_LARGE} (large)")
    print(f"{'='*60}")
    run_large = run_model_eval(
        project_client, openai_client,
        MODEL_LARGE, dataset.id,
        f"Model Eval - {MODEL_LARGE}",
    )

    # Summary
    print(f"\n{'#'*60}")
    print("MODEL COMPARISON SUMMARY")
    print(f"{'#'*60}")
    print(f"{MODEL_SMALL}: {run_small.report_url}")
    print(f"{MODEL_LARGE}: {run_large.report_url}")
    print("\nCompare in Foundry portal > Evaluation to see the difference!")
    print(f"Expected: {MODEL_LARGE} should outperform {MODEL_SMALL} on complex reasoning.")


if __name__ == "__main__":
    main()
