# Azure AI Foundry Evaluations Demo

End-to-end demo showcasing **Azure AI Foundry Evaluations** — custom evaluators, agent & model comparison, RAG groundedness, agentic process evaluation, comprehensive safety assessment, red teaming, continuous monitoring, and CI/CD integration.

## What This Demo Shows

| # | Category | Description |
|---|----------|-------------|
| 01 | **Custom Evaluators** | Prompt-based (AI judge) + code-based (deterministic) evaluators registered in the Foundry catalog |
| 02 | **Agent Setup** | Two agents (generic vs. teen-friendly persona) with Bing web search |
| 03 | **Agent Quality Eval** | Side-by-side agent comparison on quality + custom personality evaluator |
| 04 | **Model Comparison** | gpt-4.1-nano vs gpt-5.2 on hard computation & reasoning tasks |
| 05 | **Continuous Monitoring** | Automatic production monitoring rule for agent responses |
| 06 | **Red Teaming** | Automated adversarial testing across 6 risk categories with 4 attack strategies |
| 07 | **RAG Eval (Offline)** | Groundedness, relevance, and completeness on pre-recorded RAG data with hallucination detection |
| 08 | **Agent Process Eval** | Intent resolution, tool call accuracy, and task completion assessment |
| 09 | **Safety Suite** | Full safety scorecard: violence, sexual, self-harm, hate, protected materials, code vulnerability, prompt injection |
| 10 | **RAG Eval (Online)** | Live RAG agent with file search — groundedness evaluated on real document retrieval |
| 11 | **Continuous Eval Demo** | Sends conversations to the agent to trigger continuous monitoring |
| CI | **CI/CD Pipeline** | GitHub Actions workflow using `microsoft/ai-agent-evals` action |

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
uv run python 01_create_custom_evaluator.py    # Register custom evaluators (prompt + code-based)
uv run python 02_create_agents.py              # Create both agents
uv run python 03_eval_agents.py                # Agent quality eval (takes ~5 min)
uv run python 04_eval_models.py                # Model comparison (takes ~5 min)
uv run python 05_continuous_eval.py            # Set up continuous monitoring rule
uv run python 06_red_teaming.py                # Red-team the teen agent (~10-30 min)
uv run python 07_eval_rag.py                   # Offline RAG groundedness eval
uv run python 08_eval_agent_process.py         # Agent process eval (takes ~5 min)
uv run python 09_eval_safety_suite.py          # Comprehensive safety scorecard
uv run python 10_eval_rag_agent.py             # Online RAG agent eval (takes ~5 min)
uv run python 11_demo_continuous_eval.py       # Send conversations to trigger monitoring
```

## Project Structure

```
├── .env                               # Environment config (not committed)
├── .github/workflows/eval.yml         # CI/CD pipeline
├── pyproject.toml                     # Python project (uv)
├── data/
│   ├── agent-test-queries.jsonl       # Teen-oriented queries for agent eval
│   ├── model-test-queries.jsonl       # Hard computation & reasoning for model comparison
│   ├── rag-test-queries.jsonl         # RAG data with hallucinations (offline eval)
│   ├── rag-agent-test-queries.jsonl   # Queries + ground truth for live RAG agent
│   ├── techvibe-handbook.md           # TechVibe employee handbook (RAG knowledge base)
│   ├── safety-test-queries.jsonl      # Safety edge cases
│   └── github-action-data.json        # Data file for GitHub Action CI/CD
├── scripts/
│   ├── helpers.py                     # Shared config & utilities
│   ├── 01_create_custom_evaluator.py  # Register prompt-based + code-based evaluators
│   ├── 02_create_agents.py            # Create Generic & Teen agents (Bing web search)
│   ├── 03_eval_agents.py              # Agent quality evaluation
│   ├── 04_eval_models.py              # Model comparison evaluation
│   ├── 05_continuous_eval.py          # Set up continuous eval monitoring rule
│   ├── 06_red_teaming.py              # Automated adversarial red teaming
│   ├── 07_eval_rag.py                 # RAG offline evaluation (pre-recorded data)
│   ├── 08_eval_agent_process.py       # Agent process evaluation (intent, tools, tasks)
│   ├── 09_eval_safety_suite.py        # Comprehensive safety & security evaluation
│   ├── 10_eval_rag_agent.py           # RAG online evaluation (live file search agent)
│   └── 11_demo_continuous_eval.py     # Demo: trigger continuous monitoring
└── personality-eval/
    └── data-sample.jsonl              # Original sample data
```

## Naming Convention in Foundry Portal

All evaluations use a `[XX] Category - Target` naming pattern so you can immediately identify them in the Foundry portal:

| Portal Name | Type | Script |
|-------------|------|--------|
| `[03] Agent Quality - generic-assistant` | Agent quality eval | 03 |
| `[03] Agent Quality - teen-friendly-assistant` | Agent quality eval | 03 |
| `[04] Model Comparison - gpt-4.1-nano` | Model eval | 04 |
| `[04] Model Comparison - gpt-5.2` | Model eval | 04 |
| `[05] Continuous Monitoring - teen-friendly-assistant` | Continuous eval | 05 |
| `[06] Red Team - teen-friendly-assistant` | Red teaming | 06 |
| `[07] RAG Offline - Groundedness & Completeness` | RAG eval (offline) | 07 |
| `[08] Agent Process - generic-assistant` | Agent process eval | 08 |
| `[08] Agent Process - teen-friendly-assistant` | Agent process eval | 08 |
| `[09] Safety Suite - Comprehensive Assessment` | Safety eval | 09 |
| `[10] RAG Agent - rag-handbook-assistant` | RAG eval (online) | 10 |

## Step-by-Step Demo Guide

### Step 1 — Custom Evaluators (`01_create_custom_evaluator.py`)

Registers **two types of custom evaluators** in the Foundry evaluator catalog:

- **Prompt-based (AI judge)**: "Personality & Soul Evaluator" — an LLM scores responses 1–5 on how fun, warm, and teenager-friendly they are.
- **Code-based (deterministic)**: "Response Engagement Evaluator" — a Python function programmatically checks response length, formatting, and engagement signals (emojis, questions, exclamations).

After running, find both in **Foundry portal → Evaluation → Evaluator catalog**.

### Step 2 — Create Agents (`02_create_agents.py`)

Creates two Foundry agents using the same model (`gpt-4.1`) but different prompts. Both agents have **Bing web search** enabled via the Bing Grounding tool.

- **generic-assistant**: Minimal system prompt — *"You are a helpful assistant."*
- **teen-friendly-assistant**: Rich personality/soul — casual language, emojis, humor, teen-relatable examples

### Step 3 — Agent Quality Eval (`03_eval_agents.py`)

Runs both agents through 13 teenager-oriented queries with these evaluators:

- **Built-in**: Coherence, Fluency, Task Adherence, Violence
- **Custom**: Personality & Soul Evaluator

**Expected**: Teen-friendly agent scores significantly higher on personality (4–5) vs generic (1–3). Both score comparably on coherence/fluency. View and compare in **Foundry portal → Evaluation**.

### Step 4 — Model Comparison (`04_eval_models.py`)

Sends 10 **hard computation and reasoning tasks** to both `gpt-4.1-nano` and `gpt-5.2`. Evaluates with Coherence, Fluency, Relevance, custom Reasoning Depth, and custom Correctness (with ground truth).

**Expected**: gpt-4.1-nano struggles with multi-step arithmetic and formal proofs. gpt-5.2 handles them correctly. The questions are specifically designed to expose the capability gap.

### Step 5 — Continuous Monitoring (`05_continuous_eval.py`)

Sets up an automatic evaluation rule that monitors `teen-friendly-assistant` in production. When the agent responds, a sample of responses is evaluated for violence, coherence, and personality.

Visible in **Foundry portal → Monitoring → Agent Monitoring Dashboard**.

### Step 6 — Red Teaming (`06_red_teaming.py`)

Runs **automated adversarial red teaming** against the teen-friendly agent:

1. Targets 6 risk categories: Violence, Hate/Unfairness, Sexual, Self-Harm, Prohibited Actions, Sensitive Data Leakage
2. Uses 4 attack strategies: Flip, Base64, Jailbreak, IndirectJailbreak
3. Multi-turn conversations (3 turns each)
4. Reports Attack Success Rate (ASR) per category

**Expected**: Low ASR — the agent resists adversarial attempts. View in **Foundry portal → Evaluation**.

> **Note**: Red teaming takes ~10–30 minutes.

### Step 7 — RAG Offline Eval (`07_eval_rag.py`)

Evaluates pre-recorded **RAG responses** from a company knowledge base. The dataset includes **deliberately hallucinated** and **incomplete** responses to show Foundry catching issues.

- **Groundedness**: Catches hallucinated content not in the retrieved context
- **Relevance**: Measures how well the response addresses the query
- **Response Completeness**: Catches missing critical information

**Expected**: Entries with hallucinations fail Groundedness; incomplete entries fail Completeness.

### Step 8 — Agent Process Eval (`08_eval_agent_process.py`)

Evaluates **HOW agents reason and act**, not just what they output:

- **Intent Resolution**: Did the agent correctly identify the user's intent?
- **Tool Call Accuracy**: Did the agent call the right tools (Bing web search) with correct parameters?
- **Task Completion**: Did the agent fully complete the requested task?

**Expected**: Both agents resolve intent well; tool usage patterns may differ due to personality.

### Step 9 — Safety Suite (`09_eval_safety_suite.py`)

Runs the **full safety evaluator suite** against pre-recorded responses as a safety "scorecard":

- **Content Safety**: Violence, Sexual, Self-Harm, Hate & Unfairness
- **IP Protection**: Protected Materials (copyright detection)
- **Code Security**: Code Vulnerability (detects `eval()`, SQL injection, etc.)
- **Prompt Injection**: Indirect Attack / XPIA

**Expected**: Safe responses pass; the entry with `eval()` usage gets flagged for code vulnerability.

### Step 10 — RAG Online Eval (`10_eval_rag_agent.py`)

Creates a **live RAG agent** with file search over the TechVibe Solutions employee handbook, then evaluates it:

1. **Uploads** the handbook to a vector store
2. **Creates** a RAG agent with file search tool
3. **Evaluates live responses** with Groundedness, Relevance, Response Completeness, Coherence, Fluency

Foundry's Groundedness evaluator **automatically extracts context** from the agent's file search tool calls — no manual context mapping needed.

**Expected**: High scores across all evaluators (responses grounded in real documents).

### Step 11 — Continuous Eval Demo (`11_demo_continuous_eval.py`)

After setting up the monitoring rule (step 5), this script **sends 5 conversations** to the teen-friendly agent to generate responses that trigger the continuous evaluation rule.

Check results in **Foundry portal → Monitoring → Agent Monitoring Dashboard**. You can also chat with the agent directly in the **Agents playground** — every response is automatically evaluated.

> **Note**: Results may take a few minutes to appear in the dashboard.

### CI/CD — GitHub Actions (`.github/workflows/eval.yml`)

Two jobs run on push to `main` or manual trigger:

- **Agent Evaluation**: Uses `microsoft/ai-agent-evals@v3-beta` action — compares both agents with statistical significance testing
- **Model Evaluation**: Runs `04_eval_models.py` via uv

#### GitHub Setup

Set these as repository **secrets** (`Settings → Secrets and variables → Actions → Secrets`):

| Secret | Value |
|--------|-------|
| `AZURE_CLIENT_ID` | Service principal / managed identity client ID |
| `AZURE_TENANT_ID` | Entra tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

Set this as a repository **variable** (`Actions → Variables`):

| Variable | Value |
|----------|-------|
| `AZURE_AI_PROJECT_ENDPOINT` | Your Foundry project endpoint |

Configure [federated credentials](https://learn.microsoft.com/azure/developer/github/connect-from-azure-openid-connect) for passwordless auth.

## Foundry Portal Demo Tips

After running the scripts, walk through these in the portal:

1. **Evaluator catalog** → Find both custom evaluators (prompt-based + code-based)
2. **Agents** → Show all three agents and their different configurations
3. **Evaluation** → `[03]` entries: compare agent quality side-by-side, show personality score difference
4. **Evaluation** → `[04]` entries: compare model reasoning, highlight correctness gap
5. **Evaluation** → `[07]` entry: click into failed Groundedness items to see hallucinations caught
6. **Evaluation** → `[10]` entry: show live RAG with file search retrieval + groundedness
7. **Evaluation** → `[08]` entries: compare intent resolution and tool call accuracy
8. **Evaluation** → `[09]` entry: show comprehensive safety scorecard
9. **Evaluation** → `[06]` entry: show red teaming attack success rate
10. **Monitoring** → Show continuous evaluation dashboard with live metrics

## Foundry Evaluator Coverage

This demo showcases evaluators across all major categories available in Azure AI Foundry:

| Category | Evaluators Demonstrated | Script(s) |
|----------|------------------------|-----------|
| **General Purpose** | Coherence, Fluency | 03, 04 |
| **RAG** | Groundedness, Relevance, Response Completeness | 07, 10 |
| **Agent (System)** | Task Adherence, Intent Resolution, Task Completion | 03, 08 |
| **Agent (Process)** | Tool Call Accuracy | 08 |
| **Content Safety** | Violence, Sexual, Self-Harm, Hate & Unfairness | 06, 09 |
| **Security** | Code Vulnerability, Indirect Attack (XPIA), Protected Materials | 09 |
| **Agent Safety** | Prohibited Actions, Sensitive Data Leakage | 06 |
| **Custom (Prompt)** | Personality & Soul, Reasoning Depth, Correctness | 01, 03, 04 |
| **Custom (Code)** | Response Engagement | 01 |
| **Red Teaming** | 6 risk categories × 4 attack strategies | 06 |
| **Continuous Eval** | Production monitoring with auto-triggered evaluators | 05, 11 |