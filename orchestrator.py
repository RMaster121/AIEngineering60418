import asyncio
import datetime
import json
import os

import load_dotenv

import task_config
from evaluator import evaluate_blueprint_async
from llm_provider import LLMProvider, MistralProvider, LocalOllamaProvider, OpenRouterProvider
from models import AgentBlueprint

load_dotenv.load_dotenv()


async def evolution(think_provider: LLMProvider, judge_provider: LLMProvider, test_provider: LLMProvider, max_iterations: int, target_success_rate: float = 1.0):
    history = []
    best_score = -1.0
    best_blueprint = None

    def clean_name(name: str) -> str:
        return name.replace("/", "-").replace(":", "-")

    think_name = clean_name(think_provider.model_name)
    judge_name = clean_name(judge_provider.model_name)
    worker_name = clean_name(test_provider.model_name)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"audit_log_{think_name}_{judge_name}_{worker_name}_{timestamp}.txt"

    print(f"Starting Evolution using:")
    print(f" STEM_Agent:  {think_provider.model_name}")
    print(f" Judge:         {judge_provider.model_name}")
    print(f" Worker (Test): {test_provider.model_name}")
    print(f"Current Task: {task_config.TASK_DESCRIPTION}\n")
    print(f"Evaluation criteria: {task_config.EVALUATION_CRITERIA}\n")
    print(f"Audit Logs will be saved to: {log_filename}\n")

    for iteration in range(1, max_iterations + 1):
        stem_prompt = f"""
        You are an AI Architect (Stem Agent). Your goal is to write a flawless 'system_prompt' for a Target Agent.

        TASK DIRECTIVE FOR TARGET AGENT: 
        {task_config.TASK_DESCRIPTION}

        EVALUATION CRITERIA (The Judge will use this to score the Target Agent):
        {task_config.EVALUATION_CRITERIA}

        HISTORY OF JUDGE'S FEEDBACK:
        {json.dumps(history, indent=2, ensure_ascii=False) if history else "No history. This is the baseline iteration."}

        Read the Judge's feedback carefully. If the Judge says the model failed, adjust your system_prompt to fix that exact issue. Generate the new Blueprint.
        """

        try:
            print(f"--- Iteration {iteration}/{max_iterations} ---")
            print("Stem Agent is creating new agent...")

            blueprint = None
            max_stem_retries = 3

            for attempt in range(max_stem_retries):
                try:
                    blueprint = await asyncio.to_thread(
                        think_provider.generate_blueprint,
                        prompt=stem_prompt,
                        schema=AgentBlueprint,
                        temperature=0.7
                    )
                    break
                except Exception as e:
                    if attempt == max_stem_retries - 1:
                        raise Exception(f"STEM_AGENT critical failure: {e}")
                    wait_time = 5 ** attempt
                    print(f"API Error. Retrying STEM_Agent in {wait_time}s...")
                    await asyncio.sleep(wait_time)

            print(f"Strategy: {blueprint.iterations_analysis}")
            print(f"New system prompt: {blueprint.system_prompt}")
            print("Running evaluation...")

            eval_results = await evaluate_blueprint_async(blueprint, task_config.DATASET, test_provider, judge_provider)
            success_rate = eval_results["success_rate"]

            with open(log_filename, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n{'=' * 60}\n")
                log_file.write(f"ITERATION {iteration}/{max_iterations} | SUCCESS RATE: {success_rate * 100}%\n")
                log_file.write(f"{'=' * 60}\n")
                log_file.write(f"TARGET AGENT SYSTEM PROMPT:\n{blueprint.system_prompt}\n")
                log_file.write(f"TEMPERATURE: {blueprint.temperature}")
                log_file.write(f"\n--- EVALUATION DETAILS ---\n")

                for detail in eval_results.get("task_details", []):
                    log_file.write(f"TASK {detail['task_id']}:\n")
                    log_file.write(f"  Worker Output: {detail['actual']}\n")
                    log_file.write(f"  Judge Feedback: {detail['feedback']}\n")
                    log_file.write(f"  {'-' * 30}\n")

            print(f"Success Rate: {success_rate * 100}%\n")

            if success_rate > best_score:
                best_score = success_rate
                best_blueprint = blueprint

            if success_rate >= target_success_rate:
                print("Target success rate achieved!")
                break

            history.append({
                "iteration": iteration,
                "used_prompt": blueprint.system_prompt,
                "judge_feedback": eval_results["errors"]
            })

        except Exception as e:
            print(f"Critical execution error: {e}")
            break

    print(f"\nPeak Success Rate Achieved: {best_score * 100}%")
    if best_blueprint:
        print("\n=== OPTIMAL SYSTEM PROMPT ===")
        print(best_blueprint.system_prompt)
        return best_blueprint
    return None


if __name__ == "__main__":
    thinking_provider = MistralProvider(api_key=os.getenv("MISTRAL_API_KEY"), model_name="mistral-large-latest")

    judging_provider = OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY"),
                                          model_name="qwen/qwen-2.5-7b-instruct")

    testing_provider = OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY"),
                                          model_name="meta-llama/llama-3.2-3b-instruct")

    # testing_provider = LocalOllamaProvider(model_name="tinyllama")



    asyncio.run(evolution(
        think_provider=thinking_provider,
        judge_provider=judging_provider,
        test_provider=testing_provider,
        max_iterations=20
    ))