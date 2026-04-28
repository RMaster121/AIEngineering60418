import json
from abc import abstractmethod, ABC
from typing import TypeVar, Type, List

from mistralai.client.models import ResponseFormat
from openai.types import ResponseFormatJSONObject
from pydantic import BaseModel
from models import JudgeEvaluation

from openai import OpenAI
from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

T = TypeVar('T', bound=BaseModel)

class LLMProvider(ABC):
    """Abstract interface for LLM providers."""
    model_name: str

    @abstractmethod
    def generate_blueprint(self, prompt: str, schema: Type[T], temperature: float) -> T:
        """Generates the next iteration blueprint based on the provided schema."""
        pass

    @abstractmethod
    def evaluate_task(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Performs the target extraction task and returns the raw string result."""
        pass

    @abstractmethod
    def evaluate_as_judge(self, prompt: str, schema: Type[JudgeEvaluation]) -> JudgeEvaluation:
        """Method for the Judge Agent: Evaluate the target output and return a structured verdict."""
        pass


class MistralProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "mistral-large-latest"):
        from mistralai.client import Mistral
        self.client = Mistral(api_key=api_key)
        self.model_name = model_name

    def generate_blueprint(self, prompt: str, schema: Type[T], temperature: float) -> T:
        schema_info = json.dumps(schema.model_json_schema(), indent=2)

        full_prompt = (
            f"{prompt}\n\n"
            f"--- CRITICAL FORMATTING INSTRUCTION ---\n"
            f"You must return the response as a clean, valid JSON object.\n"
            f"Adhere strictly to the following JSON schema (pay attention to required fields):\n"
            f"{schema_info}\n"
        )

        response = self.client.chat.complete(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            response_format=ResponseFormat(type="json_object"),
            temperature=temperature
        )
        return schema.model_validate_json(response.choices[0].message.content)

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

    def evaluate_as_judge(self, prompt: str, schema: Type[JudgeEvaluation]) -> JudgeEvaluation:
        schema_info = json.dumps(schema.model_json_schema(), indent=2)

        full_prompt = (
            f"{prompt}\n\n"
            f"--- CRITICAL FORMATTING INSTRUCTION ---\n"
            f"You must return the response as a clean, valid JSON object.\n"
            f"Adhere strictly to the following JSON schema:\n"
            f"{schema_info}"
        )

        response = self.client.chat.complete(
            model=self.model_name,
            messages=[{"role": "user", "content": full_prompt}],
            response_format=ResponseFormat(type="json_object"),
            temperature=0.0
        )
        return schema.model_validate_json(response.choices[0].message.content)


class OpenAICompatibleProvider(LLMProvider):
    """Base class for API providers that use the official OpenAI Python SDK."""
    client: OpenAI

    def generate_blueprint(self, prompt: str, schema: Type[T], temperature: float) -> T:
        schema_info = json.dumps(schema.model_json_schema(), indent=2)
        full_prompt = f"{prompt}\n\nYou MUST return valid JSON exactly matching this schema:\n{schema_info}"

        messages: List[ChatCompletionMessageParam] = [
            ChatCompletionUserMessageParam(role="user", content=full_prompt)
        ]

        # noinspection PyTypeChecker
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format=ResponseFormatJSONObject(type="json_object"),
            temperature=temperature
        )
        return schema.model_validate_json(response.choices[0].message.content)

    def evaluate_task(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        messages: List[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(role="system", content=system_prompt),
            ChatCompletionUserMessageParam(role="user", content=user_prompt)
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature
        )
        return response.choices[0].message.content

    def evaluate_as_judge(self, prompt: str, schema: Type[JudgeEvaluation]) -> JudgeEvaluation:
        schema_info = json.dumps(schema.model_json_schema(), indent=2)
        full_prompt = f"{prompt}\n\nReturn ONLY valid JSON matching this schema:\n{schema_info}"

        messages: List[ChatCompletionMessageParam] = [
            ChatCompletionUserMessageParam(role="user", content=full_prompt)
        ]

        # noinspection PyTypeChecker
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.0
        )
        return schema.model_validate_json(response.choices[0].message.content)


class LocalOllamaProvider(OpenAICompatibleProvider):
    def __init__(self, model_name: str = "llama3.1"):
        self.client = OpenAI(
            base_url="http://localhost:11434/v1",
            api_key="ollama",
        )
        self.model_name = model_name


class OpenRouterProvider(OpenAICompatibleProvider):
    def __init__(self, api_key: str, model_name: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model_name = model_name

class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
