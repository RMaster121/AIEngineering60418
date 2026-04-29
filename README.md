# STEM Agent

**Author:** Rafał Szczerba

This project implements a "STEM Agent" architecture.
## Architecture Overview

The system utilizes a multi-agent "loop" consisting of four distinct roles:

1. **Discovery Agent**: Processes a 20% sample of the dataset to deduce the underlying task and define strict evaluation criteria. This prevents overfitting and establishes the "DNA" of the task.
2. **STEM Agent (The Architect)**: Acts as the generative brain. It analyzes historical feedback to design a "blueprint" for the worker, including the system prompt and optimal temperature.
3. **Worker Agent**: The specialized "worker" cell. It has no prior knowledge of the task until it receives the blueprint from the STEM agent to execute specific requests.
4. **Judge Agent**: An impartial evaluator that compares the Worker's output against ground truth, providing detailed reasoning for failures which serves as the motivator for the next iteration.

## Example domain
The agent was tasked with transforming unstructured customer emails into a structured JSON format containing:
- `department`: (billing, technical, shipping, general)
- `priority`: (high, medium, low)

The dataset contains various complex scenarios, from billing disputes to urgent technical outages.

## Evolutionary Results
Over five iterations, the STEM agent successfully optimized the Worker's performance, achieving a **24% improvement** in accuracy:

| Iteration | Temperature | Success Rate |
| :--- | :--- | :--- |
| 1 | 0.5 | 71% |
| 2 | 0.5 | 86% |
| 3 | 0.4 | 76% |
| 4 | 0.7 | 86% |
| **5** | **0.5** | **95%** |

## Setup and Execution

### Prerequisites
- Python 3.10+
- OpenRouter / Mistral / OpenAI API Key

### Installation
1. Clone the repository.
2. Install dependencies:
```uv sync```
3. Configure your environment:
Rename .env.example to .env and change API keys inside
4. Modify providers in ```orchestrator.py``` files according to needs (OpenRouterProvider, OpenAICompatibleProvider, LocalOllamaProvider, MistralProvider) with
```api_key=os.getenv("{PROVIDER_NAME}_API_KEY")```
```model_name="{model_name}"```
5. Run the evolution
```python orchestrator.py```
