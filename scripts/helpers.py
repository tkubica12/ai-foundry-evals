"""
Shared configuration and helper functions for all eval scripts.
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

ENDPOINT = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
MODEL_DEPLOYMENT = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4.1")
MODEL_SMALL = os.environ.get("MODEL_SMALL", "gpt-4.1-nano")
MODEL_LARGE = os.environ.get("MODEL_LARGE", "gpt-5.2")

# Resolve project root regardless of cwd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def get_clients():
    """Return (project_client, openai_client) using Entra auth."""
    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=ENDPOINT, credential=credential)
    openai_client = project_client.get_openai_client()
    return project_client, openai_client


def wait_for_run(client, eval_id, run_id, poll_interval=10):
    """Poll an evaluation run until it completes or fails. Returns the run."""
    while True:
        run = client.evals.runs.retrieve(run_id=run_id, eval_id=eval_id)
        if run.status in ("completed", "failed", "cancelled"):
            break
        print(f"  Status: {run.status} ... waiting {poll_interval}s")
        time.sleep(poll_interval)
    return run


def print_run_results(client, eval_id, run):
    """Print summary and per-item results for an evaluation run."""
    print(f"\n{'='*60}")
    print(f"Run: {run.id}  |  Status: {run.status}")
    if hasattr(run, "result_counts") and run.result_counts:
        print(f"Results: {run.result_counts}")
    if hasattr(run, "per_testing_criteria_results") and run.per_testing_criteria_results:
        for tc in run.per_testing_criteria_results:
            print(f"  {tc}")
    print(f"Report URL: {run.report_url}")
    print(f"{'='*60}\n")

    # Print individual output items
    try:
        items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_id))
        for item in items[:5]:  # Show first 5
            print(f"  Item {item.id}:")
            if hasattr(item, "results") and item.results:
                for r in item.results:
                    if isinstance(r, dict):
                        name = r.get("name", "?")
                        score = r.get("score", r.get("label", "?"))
                        passed = r.get("passed", "?")
                    else:
                        name = getattr(r, "name", "?")
                        score = getattr(r, "score", getattr(r, "label", "?"))
                        passed = getattr(r, "passed", "?")
                    print(f"    {name}: score={score}, passed={passed}")
    except Exception as e:
        print(f"  (Could not list output items: {e})")
