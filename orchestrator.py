import asyncio
import datetime
import os

import load_dotenv

import task_config
from evaluator import evaluate_blueprint_async
from llm_provider import *
from models import AgentBlueprint, RulesBlueprint

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
    print(f" STEM_Agent:    {think_provider.model_name}")
    print(f" Judge:         {judge_provider.model_name}")
    print(f" Worker (Test): {test_provider.model_name}")

    if len(task_config.DATASET) <= 0: raise Exception("No dataset provided")

    sample_env = [{"input": sample["input_text"], "expected": sample["expected"]} for sample in task_config.DATASET[:max(round(len(task_config.DATASET) * 0.2), 1)]]
    discovery_prompt = f"""
        You are an AI Architect. You are placed in a new environment with no prior instructions.
        Analyze these environmental samples (inputs and expected states):

        {json.dumps(sample_env, indent=2)}

        1. Deduce the main task that needs to be solved.
        2. Write strict evaluation criteria for a Judge Agent to verify if future solutions are correct.
        """

    rules_blueprint: RulesBlueprint = await asyncio.to_thread(
        think_provider.generate_blueprint,
        prompt=discovery_prompt,
        schema=RulesBlueprint,
        temperature=0.4
    )


    print(f"Current Task: {rules_blueprint.task_description}\n")
    print(f"Evaluation criteria: {rules_blueprint.evaluation_criteria}\n")
    print(f"Audit Logs will be saved to: {log_filename}\n")

    with open(log_filename, "w", encoding="utf-8") as log_file:
        log_file.write("=== STEM AGENT EVOLUTION AUDIT LOG ===\n")
        log_file.write(f"Timestamp:    {timestamp}\n")
        log_file.write(f"STEM Agent:   {think_provider.model_name}\n")
        log_file.write(f"Judge Agent:  {judge_provider.model_name}\n")
        log_file.write(f"Worker Agent: {test_provider.model_name}\n")
        log_file.write("=" * 60 + "\n")
        log_file.write(f"Task Description:\n{rules_blueprint.task_description}\n\n")
        log_file.write(f"Evaluation Criteria:\n{rules_blueprint.evaluation_criteria}\n")
        log_file.write("=" * 60 + "\n\n")


    for iteration in range(1, max_iterations + 1):
        stem_prompt = f"""
        You are an AI Architect (Stem Agent). Your goal is to write a flawless 'system_prompt' for a Target Agent.

        TASK DIRECTIVE FOR TARGET AGENT: 
        {rules_blueprint.task_description}

        EVALUATION CRITERIA (The Judge will use this to score the Target Agent):
        {rules_blueprint.evaluation_criteria}

        HISTORY OF JUDGE'S FEEDBACK:
        {json.dumps(history, indent=2, ensure_ascii=False) if history else "No history. This is the baseline iteration."}
        
        CRITICAL INSTRUCTIONS FOR UPDATING THE TARGET AGENT:
        1. SELECTING ARCHITECTURE: 
           - 'single_shot': Use if the task is extremely simple.
           - 'cot': Use if the model needs step-by-step reasoning (Chain-of-Thought).
           - 'self_reflection': Use if the model needs to draft an answer and critique itself before final output. 
        2. STRUCTURED OUTPUT (CRITICAL):
           Regardless of the architecture you choose, the Target Agent MUST return a single, valid JSON object. 
           If you choose 'cot', YOU MUST INSTRUCT it to use a "reasoning" key ALWAYS. NEVER make reasoning optional.
           If you choose 'self_reflection', YOU MUST INSTRUCT it to use "draft" and "critique" keys ALWAYS.
           The final target data MUST ALWAYS be placed strictly inside a "result" key.
           
           Example format you must demand from the Target Agent:
           ```json
           {{
               "reasoning": "mandatory step-by-step analysis...", 
                "result": {{"...":"..."}}
           }}
           ```
           or
           ```
           {{
                "draft": "first draft", 
                "critique": "critique of first draft", 
                "result": {{"...":"..."}}
           }}
           ```
        3. ESTABLISH CORE PRINCIPLES (MANDATORY RULES SECTION): 
           You MUST include a specific section called "CRITICAL RULES" in the system_prompt you generate for the Target Agent.
           Read the Judge's feedback and write 2-3 absolute, concrete rules to prevent previous mistakes.
           Example rules you should write if applicable:
           - "RULE: The threat_vector must be exactly ONE string from the allowed list. Do not combine them."
           - "RULE: If a suspicious link or attachment is present, it takes absolute priority over urgency_manipulation."
           DO NOT rely on generic advice. Explicitly list the rules.        
        4. AVOID OVERLOADING: Do not give the Target Agent too many rules. Keep the system prompt concise, structured, and easy to follow for a smaller AI.        
        5. DECISION CONSISTENCY (CRITICAL): Establish a SINGLE, consistent decision policy and refine it incrementally.
        
        Read the Judge's feedback carefully. If the Judge says the model failed, adjust your system_prompt to fix that exact issue. Generate the new Blueprint.
        """

        try:
            print(f"--- Iteration {iteration}/{max_iterations} ---")
            print("Stem Agent is creating new agent...")

            blueprint: AgentBlueprint | None = None
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
            print(f"Architecture Selected: {blueprint.architecture}")
            print(f"Prompt: {blueprint.system_prompt}")
            print(f"Temperature: {blueprint.temperature}")
            print("Running evaluation...")

            eval_results = await evaluate_blueprint_async(blueprint, rules_blueprint, task_config.DATASET, test_provider, judge_provider)
            success_rate = eval_results["success_rate"]

            with open(log_filename, "a", encoding="utf-8") as log_file:
                log_file.write(f"\n{'=' * 60}\n")
                log_file.write(f"ITERATION {iteration}/{max_iterations} | SUCCESS RATE: {success_rate * 100}%\n")
                log_file.write(f"{'=' * 60}\n")
                log_file.write(f"STEM AGENT STRATEGY (Analysis):\n")
                for obs in blueprint.iterations_analysis:
                    log_file.write(f" - {obs}\n")
                log_file.write("\n")
                log_file.write(f"TARGET AGENT SYSTEM PROMPT:\n{blueprint.system_prompt}\n")
                log_file.write(f"TEMPERATURE: {blueprint.temperature}\n")
                log_file.write(f"SELECTED STRATEGY: {blueprint.architecture}\n")
                log_file.write(f"\n--- EVALUATION DETAILS ---\n")

                for detail in eval_results.get("task_details", []):
                    log_file.write(f"TASK {detail['task_id']}:\n")
                    log_file.write(f"  Worker Output: {detail['actual']}\n")
                    log_file.write(f"  Judge Feedback: {detail['feedback']}\n")
                    log_file.write(f"  Thoughts: {detail['thoughts']}")
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
        print(f"\n=== OPTIMAL TEMPERATURE = {best_blueprint.temperature} ===")
        print(f"\n=== OPTIMAL ARCHITECTURE = {best_blueprint.architecture} ===")
        print("\n=== OPTIMAL SYSTEM PROMPT ===")
        print(best_blueprint.system_prompt)

        with open(log_filename, "a", encoding="utf-8") as log_file:
            log_file.write(f"\nPeak Success Rate Achieved: {best_score * 100}%\n")
            log_file.write(f"\n=== OPTIMAL TEMPERATURE = {best_blueprint.temperature} ===\n")
            log_file.write(f"\n=== OPTIMAL ARCHITECTURE = {best_blueprint.architecture} ===\n")
            log_file.write("\n=== OPTIMAL SYSTEM PROMPT ===\n")
            log_file.write(best_blueprint.system_prompt)

        return best_blueprint
    return None


if __name__ == "__main__":
    thinking_provider = OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY"),
                                          model_name="openai/gpt-4o-mini@preset/open-provider")

    judging_provider = OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY"),
                                              model_name="qwen/qwen-2.5-7b-instruct")

    testing_provider = OpenRouterProvider(api_key=os.getenv("OPENROUTER_API_KEY"),
                                          model_name="meta-llama/llama-3.2-3b-instruct")


    asyncio.run(evolution(
        think_provider=thinking_provider,
        judge_provider=judging_provider,
        test_provider=testing_provider,
        max_iterations=5
    ))