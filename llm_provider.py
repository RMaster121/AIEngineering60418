import json
from abc import abstractmethod, ABC
from models import AgentBlueprint, JudgeEvaluation
from openai import OpenAI


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    model_name: str

    @abstractmethod
    def generate_blueprint(self, prompt: str, schema: type[AgentBlueprint], temperature: float) -> AgentBlueprint:
        """Generates the next iteration blueprint containing analysis, temperature, and system prompt."""
        pass

    @abstractmethod
    def evaluate_task(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Performs the target extraction task and returns the raw string result."""
        pass

    @abstractmethod
    def evaluate_as_judge(self, prompt: str, schema: type[JudgeEvaluation]) -> JudgeEvaluation:
        """Method for the Judge Agent: Evaluate the target output and return a structured verdict."""
        pass


class MistralProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "mistral-large-latest"):
        from mistralai.client import Mistral
        self.client = Mistral(api_key=api_key)
        self.model_name = model_name

    def generate_blueprint(self, prompt: str, schema: type[AgentBlueprint], temperature: float) -> AgentBlueprint:
        example_json = {
            "iterations_analysis": ["Observation 1", "Observation 2"],
            "temperature": 0.5,
            "system_prompt": "Your optimized system prompt here"
        }

        full_prompt = (
            f"{prompt}\n\n"
            f"--- CRITICAL FORMATTING INSTRUCTION ---\n"
            f"You must return the response as a clean, valid JSON object.\n"
            f"DO NOT return schema definitions (do not use words like 'properties' or 'type').\n"
            f"Return the populated fields in exactly the following structure:\n"
            f"{json.dumps(example_json, indent=2)}"
        )

        response = self.client.chat.complete(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"},
            temperature=temperature
        )

        raw_json = response.choices[0].message.content
        return schema.model_validate_json(raw_json)

    def evaluate_task(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.chat.complete(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content

    def evaluate_as_judge(self, prompt: str, schema: type[JudgeEvaluation]) -> JudgeEvaluation:
        example_json = {
            "is_correct": False,
            "feedback": "The model extracted 'return' instead of 'complaint', but this is an acceptable synonym. However, frustration_level was 5 instead of 10."
        }

        full_prompt = (
            f"{prompt}\n\n"
            f"--- CRITICAL FORMATTING INSTRUCTION ---\n"
            f"You must return the response as a clean, valid JSON object.\n"
            f"Return the populated fields in exactly the following structure:\n"
            f"{json.dumps(example_json, indent=2)}"
        )

        response = self.client.chat.complete(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return schema.model_validate_json(response.choices[0].message.content)


class LocalOllamaProvider(LLMProvider):
    def __init__(self, model_name: str = "llama3.1"):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
        self.model_name = model_name

    def generate_blueprint(self, prompt: str, schema: type[AgentBlueprint], temperature: float) -> AgentBlueprint:
        example_json = {
            "iterations_analysis": ["Obs 1", "Obs 2"],
            "temperature": 0.5,
            "system_prompt": "prompt"
        }
        full_prompt = f"{prompt}\n\nYou MUST return valid JSON exactly like this:\n{json.dumps(example_json)}"

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"},
            temperature=temperature
        )
        return schema.model_validate_json(response.choices[0].message.content)

    def evaluate_task(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=temperature
        )
        return response.choices[0].message.content

    def evaluate_as_judge(self, prompt: str, schema: type[JudgeEvaluation]) -> JudgeEvaluation:
        example_json = {
            "is_correct": False,
            "feedback": "Reason for failure."
        }
        full_prompt = f"{prompt}\n\nReturn ONLY valid JSON matching this structure:\n{json.dumps(example_json)}"

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return schema.model_validate_json(response.choices[0].message.content)


class OpenRouterProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model_name = model_name

    def generate_blueprint(self, prompt: str, schema: type[AgentBlueprint], temperature: float) -> AgentBlueprint:
        example_json = {
            "iterations_analysis": ["Obs 1", "Obs 2"],
            "temperature": 0.5,
            "system_prompt": "prompt"
        }
        full_prompt = f"{prompt}\n\nYou MUST return valid JSON exactly like this:\n{json.dumps(example_json)}"

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"},
            temperature=temperature
        )
        return schema.model_validate_json(response.choices[0].message.content)

    def evaluate_task(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content

    def evaluate_as_judge(self, prompt: str, schema: type[JudgeEvaluation]) -> JudgeEvaluation:
        example_json = {
            "is_correct": False,
            "feedback": "Reason for failure."
        }
        full_prompt = f"{prompt}\n\nReturn ONLY valid JSON matching this structure:\n{json.dumps(example_json)}"

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return schema.model_validate_json(response.choices[0].message.content)