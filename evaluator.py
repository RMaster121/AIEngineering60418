import asyncio
import json
import re
import sys
import os
from llm_provider import LLMProvider
from models import JudgeEvaluation, AgentBlueprint, RulesBlueprint

if os.name == 'nt':
    os.system('color')

class TerminalDashboard:
    """Manages the live rendering of task states in the terminal."""

    def __init__(self, task_ids):
        self.states = {tid: "⏳ Waiting in queue..." for tid in task_ids}
        self.lines_printed = 0
        self.lock = asyncio.Lock()

    async def update(self, task_id: int, new_state: str):
        async with self.lock:
            self.states[task_id] = new_state
            self.render()

    def render(self):
        if self.lines_printed > 0:
            sys.stdout.write(f"\r\033[{self.lines_printed}A")

        output = "[Task Monitor]\033[K\n"
        for tid, state in self.states.items():
            output += f"  Task {tid:02d}: {state}\033[K\n"

        sys.stdout.write(output)
        sys.stdout.flush()
        self.lines_printed = len(self.states) + 1


def extract_clean_json(raw_text: str) -> dict[str, str]:
    """Extracts clean result"""
    match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
    json_str = match.group(1) if match else raw_text
    json_str = json_str.strip().strip("`")

    try:
        parsed_data = json.loads(json_str)
        reasoning = parsed_data.get("reasoning") or parsed_data.get("critique") or parsed_data.get("draft") or "No thinking process captured."
        result = parsed_data.get("result", parsed_data)

        return {
            "reasoning": reasoning,
            "result_json_str": json.dumps(result)
        }

    except json.JSONDecodeError:
        return {"reasoning": "Parse Error", "result_json_str": raw_text.strip()}

async def evaluate_single_item(blueprint: AgentBlueprint, rules: RulesBlueprint, item, test_provider: LLMProvider, judge_provider: LLMProvider,
                               dashboard: TerminalDashboard) -> dict | None:
    max_retries = 3
    actual_output = None
    actual_reasoning = "No reasoning captured."
    task_id = item['id']

    await dashboard.update(task_id, "Worker: Generating response...")
    for attempt in range(max_retries):
        try:
            actual_output_raw = await asyncio.to_thread(
                test_provider.evaluate_task,
                system_prompt=blueprint.system_prompt,
                user_prompt=item["input_text"],
                temperature=blueprint.temperature
            )
            extracted = extract_clean_json(actual_output_raw)
            actual_reasoning = extracted["reasoning"]
            actual_output = extracted["result_json_str"]
            break
        except Exception as e:
            if attempt == max_retries - 1:
                await dashboard.update(task_id, f"Worker Critical Error: {type(e).__name__}")
                return {"success": False, "error": f"[Worker Task {task_id}] Failed: {str(e)}"}
            wait_time = 5 ** attempt
            await dashboard.update(task_id, f"Worker API error. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

    if not actual_output:
        await dashboard.update(task_id, "Worker returned empty output.")
        return {"success": False, "error": f"[Task {task_id}] Worker returned empty output."}

    await dashboard.update(task_id, "Judge: Analyzing output...")
    judge_prompt = f"""
        You are an impartial AI Evaluator.

        TASK INFERRED BY STEM ARCHITECT:
        {rules.task_description}

        YOUR EVALUATION CRITERIA (Strictly follow these):
        {rules.evaluation_criteria}

        User Input: "{item['input_text']}"
        Expected Output (Ground Truth): "{item['expected']}"

        Target Agent's Reasoning: "{actual_reasoning}"
        Target Agent's Final Output: "{actual_output}"

        Evaluate if the Final Output successfully fulfills the task compared to the Expected Output.
        CRITICAL: If the Output is incorrect, read the "Target Agent's Reasoning" to determine exactly WHERE its logic failed. Mention this logical flaw explicitly in your feedback.        """

    for attempt in range(max_retries):
        try:
            evaluation = await asyncio.to_thread(
                judge_provider.evaluate_as_judge,
                prompt=judge_prompt,
                schema=JudgeEvaluation
            )

            if evaluation.is_correct:
                await dashboard.update(task_id, "Success: Approved by Judge")
                return {
                    "success": True,
                    "error": None,
                    "details": {"task_id": task_id, "actual": actual_output, "feedback": "Approved", "thoughts": actual_reasoning}
                }
            else:
                await dashboard.update(task_id, "Failed: Rejected by Judge")
                error_msg = f"[Task {task_id}] Judge Feedback: {evaluation.feedback} (Worker Output: '{actual_output}')"
                return {
                    "success": False,
                    "error": error_msg,
                    "details": {"task_id": task_id, "actual": actual_output, "feedback": evaluation.feedback, "thoughts": actual_reasoning}
                }

        except Exception as e:
            if attempt == max_retries - 1:
                await dashboard.update(task_id, f"Judge Critical Error: {type(e).__name__}")
                return {
                    "success": False,
                    "error": f"[Judge Task {task_id}] Failed: {str(e)}",
                    "details": {"task_id": task_id, "actual": actual_output, "feedback": "Judge API Crashed"}
                }
            wait_time = 2 ** attempt
            await dashboard.update(task_id, f"Judge API error. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)
    return None


async def evaluate_blueprint_async(blueprint: AgentBlueprint, rules: RulesBlueprint, dataset, test_provider: LLMProvider, judge_provider: LLMProvider) -> dict:
    print("\n")

    task_ids = [item['id'] for item in dataset]
    dashboard = TerminalDashboard(task_ids)
    dashboard.render()

    tasks = [evaluate_single_item(blueprint, rules, item, test_provider, judge_provider, dashboard) for item in dataset]
    results = await asyncio.gather(*tasks)

    success_count = sum(1 for r in results if r["success"])
    error_logs = [r["error"] for r in results if not r["success"]]
    task_details = [r["details"] for r in results if r and "details" in r]

    return {
        "success_rate": success_count / len(dataset) if len(dataset) > 0 else 0.0,
        "errors": error_logs,
        "task_details": task_details
    }