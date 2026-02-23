# Azure AI Foundry Evaluations Demo

End-to-end demo showcasing **Azure AI Foundry Evaluations** — agent evaluation with custom personality evaluator, model comparison, continuous evaluation, and CI/CD integration.

## What This Demo Shows

| Demo | Description |
|------|-------------|
| **Custom Evaluator** | Prompt-based "Personality & Soul" evaluator registered in the Foundry evaluator catalog |
| **Agent Comparison** | Two agents (generic vs. teen-friendly persona) with Bing web search, evaluated side-by-side |
| **Model Comparison** | gpt-4.1-nano vs gpt-5.2 on hard computation & reasoning tasks |
| **Red Teaming** | Automated adversarial testing of the teen-friendly agent across 6 risk categories |
| **Continuous Eval** | Automatic production monitoring rule for agent responses |
| **CI/CD** | GitHub Actions workflow using `microsoft/ai-agent-evals` action |

## Prerequisites

- Azure subscription with an AI Foundry project
- `az login` completed (Entra / DefaultAzureCredential)
- [uv](https://docs.astral.sh/uv/) package manager installed
- Model deployments: `gpt-4.1`, `gpt-4.1-nano`, `gpt-5.2`

## Quick Start

```bash
# Install dependencies
uv sync

# Configure (edit .env or export vars)
export AZURE_AI_PROJECT_ENDPOINT="https://sw-v2-project-resource.services.ai.azure.com/api/projects/sw-v2-project"
export AZURE_AI_MODEL_DEPLOYMENT_NAME="gpt-4.1"

# Run all steps sequentially
cd scripts
uv run python 01_create_custom_evaluator.py   # Register personality evaluator
uv run python 02_create_agents.py              # Create both agents
uv run python 03_eval_agents.py                # Evaluate agents (takes ~5 min)
uv run python 04_eval_models.py                # Compare models (takes ~5 min)
uv run python 05_continuous_eval.py            # Set up continuous monitoring
uv run python 06_red_teaming.py                # Red-team the teen agent (~10-30 min)
```

## Project Structure

```
├── .env                              # Environment config (not committed)
├── .github/workflows/eval.yml        # CI/CD pipeline
├── pyproject.toml                    # Python project (uv)
├── data/
│   ├── agent-test-queries.jsonl      # Teen-oriented queries for agent eval (incl. web-search)
│   ├── model-test-queries.jsonl      # Hard computation & reasoning for model comparison
│   └── github-action-data.json       # Data file for GitHub Action
├── scripts/
│   ├── helpers.py                    # Shared config & utilities
│   ├── 01_create_custom_evaluator.py # Register personality evaluator
│   ├── 02_create_agents.py           # Create Generic & Teen agents (with Bing web search)
│   ├── 03_eval_agents.py             # Run agent evaluations
│   ├── 04_eval_models.py             # Run model comparison
│   ├── 05_continuous_eval.py         # Set up continuous eval rule
│   └── 06_red_teaming.py             # Automated adversarial red teaming
└── personality-eval/
    └── data-sample.jsonl             # Original sample data
```

## Step-by-Step Demo Guide

### 1. Custom Personality Evaluator (`01_create_custom_evaluator.py`)

Registers a **prompt-based evaluator** in the Foundry evaluator catalog that scores responses 1–5 on how fun, warm, and teenager-friendly they are. After running, find it in **Foundry portal → Evaluation → Evaluator catalog**.

### 2. Create Agents (`02_create_agents.py`)

Creates two Foundry agents using the same model (`gpt-4.1`) but different prompts. Both agents have **Bing web search** enabled via the Bing Grounding tool, allowing them to search the web for current information.

- **Generic_Assistant**: Minimal system prompt — *"You are a helpful assistant."*
- **Teen_Friendly_Assistant**: Rich personality/soul — casual language, emojis, humor, teen-relatable examples

Agent names: `generic-assistant`, `teen-friendly-assistant`

### 3. Agent Evaluation (`03_eval_agents.py`)

Runs both agents through the same 13 teenager-oriented queries (including current-events questions that exercise the Bing web search tool) with these evaluators:

- **Built-in**: Coherence, Fluency, Task Adherence, Violence
- **Custom**: Personality & Soul Evaluator

**Expected result**: Teen_Friendly_Assistant scores significantly higher on personality (4–5) while Generic_Assistant scores lower (1–3). Both agents should score comparably on coherence and fluency.

View and compare results in **Foundry portal → Evaluation**.

### 4. Model Comparison (`04_eval_models.py`)

Sends 10 **hard computation and reasoning tasks** (math proofs, algorithm tracing, number conversions, RSA encryption, combinatorics, etc.) to both `gpt-4.1-nano` and `gpt-5.2`. Evaluates with Coherence, Fluency, Relevance, and a **custom Reasoning Depth evaluator**.

**Expected result**: gpt-4.1-nano struggles with multi-step arithmetic, precise algorithm tracing, and formal proofs — producing lower Reasoning Depth scores (1–3). gpt-5.2 handles them correctly (4–5). The questions are specifically designed to expose the capability gap between small and large models.

### 5. Continuous Evaluation (`05_continuous_eval.py`)

Sets up an automatic evaluation rule that monitors Teen_Friendly_Assistant in production. When the agent responds, a sample of those responses is evaluated for violence, coherence, and personality — visible in **Foundry portal → Monitoring**.

### 6. Red Teaming (`06_red_teaming.py`)

Runs **automated adversarial red teaming** against the teen-friendly agent using Azure AI Foundry's red teaming service. The system:

1. Generates adversarial prompts targeting 6 risk categories: Violence, Hate/Unfairness, Sexual content, Self-Harm, Prohibited Actions, Sensitive Data Leakage
2. Applies multiple attack strategies: Baseline, Flip, Base64, Jailbreak, Crescendo, Multi-Turn
3. Sends adversarial prompts to the agent in multi-turn conversations (3 turns each)
4. Evaluates the agent's responses for safety violations
5. Reports the Attack Success Rate (ASR) per risk category

**Expected result**: A well-designed teen-friendly assistant should have a low ASR, demonstrating it resists adversarial attempts. View results in **Foundry portal → Red Teaming**.

> **Note**: Red teaming takes ~10–30 minutes to complete.

### 7. GitHub Actions CI/CD (`.github/workflows/eval.yml`)

Two jobs:
- **Agent Evaluation** using `microsoft/ai-agent-evals@v3-beta` action — compares both agents with statistical significance testing
- **Model Evaluation** using Python scripts via uv

#### GitHub Setup

Set these as repository variables (`Settings → Secrets and variables → Actions → Variables`):

| Variable | Value |
|----------|-------|
| `AZURE_AI_PROJECT_ENDPOINT` | `https://sw-v2-project-resource.services.ai.azure.com/api/projects/sw-v2-project` |
| `AZURE_CLIENT_ID` | Service principal client ID |
| `AZURE_TENANT_ID` | Entra tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

Configure [federated credentials](https://learn.microsoft.com/azure/developer/github/connect-from-azure-openid-connect) for passwordless auth.

## Foundry Portal Demo Tips

After running the scripts, show these in the portal:

1. **Evaluator catalog** → Find "Personality & Soul Evaluator" custom evaluator
2. **Agents** → Show both agents and their different system prompts
3. **Evaluation** → Compare agent runs side-by-side, show per-row scores
4. **Evaluation** → Compare model runs, highlight score differences
5. **Monitoring** → Show continuous evaluation rule configuration