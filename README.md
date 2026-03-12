# Azure AI Foundry Evaluations & Red Teaming Demo

Comprehensive demo of **Azure AI Foundry** evaluation and red teaming capabilities. Designed for customer-facing presentations — run the scripts, then walk through results in the Foundry portal.

## Evaluation Coverage

| Category | What We Demo | Foundry Evaluators Used | Script |
|----------|-------------|------------------------|--------|
| **Agent Quality** | Compare generic vs teen-friendly agent | Coherence, Fluency, Task Adherence, Violence + custom Personality | 03 |
| **Model Comparison** | gpt-4.1-nano vs gpt-5.2 on hard reasoning | Coherence, Fluency, Relevance + custom Reasoning Depth & Correctness | 04 |
| **RAG (Offline)** | Detect hallucinations in pre-recorded RAG responses | Groundedness, Relevance, Response Completeness | 07 |
| **RAG (Online)** | Live RAG agent with file search over a knowledge base | Groundedness, Relevance, Response Completeness, Coherence, Fluency | 10 |
| **Agent Process** | Evaluate HOW agents reason, not just output | Intent Resolution, Tool Call Accuracy, Task Completion | 08 |
| **Safety Suite** | Full safety scorecard on pre-recorded data | Violence, Sexual, Self-Harm, Hate, Protected Materials, Code Vulnerability, Indirect Attack | 09 |
| **Red Teaming** | Automated adversarial attacks on teen agent | 6 risk categories × 4 attack strategies (Flip, Base64, Jailbreak, IndirectJailbreak) | 06 |
| **Custom Evaluators** | Prompt-based (AI judge) + code-based (deterministic) | Personality & Soul, Response Engagement | 01 |
| **Continuous Monitoring** | Auto-evaluate every agent response in production | Violence, Coherence, Personality (via monitoring rule) | 05, 11 |
| **CI/CD** | GitHub Actions runs evals on every push | Agent quality + model comparison in pipeline | CI |

## Prerequisites

- Azure subscription with an AI Foundry project
- `az login` completed (Entra / DefaultAzureCredential)
- [uv](https://docs.astral.sh/uv/) package manager
- Model deployments: `gpt-4.1`, `gpt-4.1-nano`, `gpt-5.2`

## Quick Start

```bash
uv sync

# Configure
export AZURE_AI_PROJECT_ENDPOINT="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"

cd scripts
uv run python 01_create_custom_evaluator.py    # Custom evaluators (prompt + code-based)
uv run python 02_create_agents.py              # Create agents
uv run python 03_eval_agents.py                # Agent quality eval (~5 min)
uv run python 04_eval_models.py                # Model comparison (~10 min)
uv run python 05_continuous_eval.py            # Set up monitoring rule
uv run python 06_red_teaming.py                # Red teaming (~10-30 min)
uv run python 07_eval_rag.py                   # RAG offline eval
uv run python 08_eval_agent_process.py         # Agent process eval (~5 min)
uv run python 09_eval_safety_suite.py          # Safety scorecard
uv run python 10_eval_rag_agent.py             # RAG online eval (~5 min)
uv run python 11_demo_continuous_eval.py       # Trigger continuous monitoring
```

## Demo Walkthrough

### 1. Setup (scripts 01–02)

**Script 01** registers two custom evaluators in the Foundry catalog:
- **Personality & Soul** (prompt-based) — LLM judges how teen-friendly the response is (1–5)
- **Response Engagement** (code-based) — Python function checks length, emojis, formatting

**Script 02** creates two agents with Bing web search — one generic, one with a fun teen personality.

> **Show in portal**: Evaluator catalog → both custom evaluators; Agents → compare system prompts

### 2. Agent Quality Eval (script 03)

Compares both agents on 13 teen-oriented queries. The teen agent scores 4–5 on Personality while the generic agent scores 1–3. Both score equally on coherence/fluency.

> **Show in portal**: Evaluation → `[03] Agent Quality` entries → compare side-by-side

### 3. Model Comparison (script 04)

Tests gpt-4.1-nano vs gpt-5.2 on hard math/reasoning tasks with ground-truth answers. The small model fails on complex arithmetic; the large model handles it.

> **Show in portal**: Evaluation → `[04] Model Comparison` entries → highlight Correctness gap

### 4. RAG Evaluation (scripts 07 + 10)

**Offline (07)**: Pre-recorded responses with **deliberate hallucinations** — Foundry's Groundedness evaluator catches them (3 failures). Great for showing hallucination detection.

**Online (10)**: Creates a live RAG agent with file search over an employee handbook. Evaluates real responses — all pass because the agent retrieves actual documents.

> **Show in portal**: Evaluation → `[07] RAG Offline` → click failed items to show hallucinations; then `[10] RAG Agent` → show perfect scores with real retrieval

### 5. Agent Process Eval (script 08)

Evaluates the reasoning process: did the agent understand intent, call the right tools, complete the task? Both agents score well on all three metrics.

> **Show in portal**: Evaluation → `[08] Agent Process` entries

### 6. Safety Suite (script 09)

Runs 7 safety evaluators in one pass. All safe responses pass; the entry with `eval()` code gets flagged for code vulnerability.

> **Show in portal**: Evaluation → `[09] Safety Suite` → show the flagged code vulnerability

### 7. Red Teaming (script 06)

Automated adversarial testing with 4 attack strategies across 6 risk categories. The teen agent resists all attacks (0% attack success rate).

> **Show in portal**: Evaluation → `[06] Red Team` → show attack success rates. Takes ~10-30 min to run.

### 8. Continuous Monitoring (scripts 05 + 11)

**Script 05** creates a monitoring rule. **Script 11** sends conversations to trigger it. Every agent response is automatically evaluated for violence, coherence, and personality. You can also chat with the agent in the **Agents playground** — all responses are auto-evaluated.

> **Show in portal**: Monitoring → Agent Monitoring Dashboard → show live evaluation metrics

### 9. CI/CD (GitHub Actions)

Two jobs run on push to `main`: agent quality eval + model comparison. Both use federated credentials for passwordless auth.

> **Show in GitHub**: Actions tab → green workflow run → evaluation results in logs

## Naming Convention

All evals use `[XX] Category - Target` so they're easy to find in the portal:

| Portal Name | Script |
|-------------|--------|
| `[03] Agent Quality - generic-assistant` | 03 |
| `[03] Agent Quality - teen-friendly-assistant` | 03 |
| `[04] Model Comparison - gpt-4.1-nano` | 04 |
| `[04] Model Comparison - gpt-5.2` | 04 |
| `[05] Continuous Monitoring - teen-friendly-assistant` | 05 |
| `[06] Red Team - teen-friendly-assistant` | 06 |
| `[07] RAG Offline - Groundedness & Completeness` | 07 |
| `[08] Agent Process - generic-assistant` | 08 |
| `[08] Agent Process - teen-friendly-assistant` | 08 |
| `[09] Safety Suite - Comprehensive Assessment` | 09 |
| `[10] RAG Agent - rag-handbook-assistant` | 10 |

## Project Structure

```
├── .github/workflows/eval.yml         # CI/CD pipeline
├── pyproject.toml                     # Python dependencies (uv)
├── data/
│   ├── agent-test-queries.jsonl       # Teen-oriented queries for agent eval
│   ├── model-test-queries.jsonl       # Hard computation & reasoning tasks
│   ├── rag-test-queries.jsonl         # RAG data with hallucinations (offline)
│   ├── rag-agent-test-queries.jsonl   # Queries for live RAG agent
│   ├── techvibe-handbook.md           # Employee handbook (RAG knowledge base)
│   ├── safety-test-queries.jsonl      # Safety edge cases
│   └── github-action-data.json        # CI/CD eval data
├── scripts/
│   ├── helpers.py                     # Shared config & utilities
│   ├── 01_create_custom_evaluator.py  # Custom evaluators (prompt + code)
│   ├── 02_create_agents.py            # Create agents (generic + teen)
│   ├── 03_eval_agents.py              # Agent quality eval
│   ├── 04_eval_models.py              # Model comparison eval
│   ├── 05_continuous_eval.py          # Continuous monitoring rule
│   ├── 06_red_teaming.py              # Red teaming
│   ├── 07_eval_rag.py                 # RAG offline eval
│   ├── 08_eval_agent_process.py       # Agent process eval
│   ├── 09_eval_safety_suite.py        # Safety suite eval
│   ├── 10_eval_rag_agent.py           # RAG online eval (file search)
│   └── 11_demo_continuous_eval.py     # Trigger continuous monitoring
└── personality-eval/
    └── data-sample.jsonl
```

## CI/CD Setup

Set repository **secrets** (`Settings → Secrets and variables → Actions → Secrets`):

| Secret | Value |
|--------|-------|
| `AZURE_CLIENT_ID` | Managed identity client ID |
| `AZURE_TENANT_ID` | Entra tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

Set repository **variable** (`Actions → Variables`):

| Variable | Value |
|----------|-------|
| `AZURE_AI_PROJECT_ENDPOINT` | Your Foundry project endpoint |

Configure [federated credentials](https://learn.microsoft.com/azure/developer/github/connect-from-azure-openid-connect) for passwordless auth.