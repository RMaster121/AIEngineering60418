from pydantic import BaseModel, Field

class AgentBlueprint(BaseModel):
    iterations_analysis: list[str] = Field(
        description="Analyze the ENTIRE provided history of the Judge's feedback. Identify why previous prompts failed and state your strategy for this iteration."
    )
    temperature: float = Field(
        description="Suggested temperature for the Target Agent. Use lower values for precision, higher for creativity.",
        ge=0.01,
        le=1.99
    )
    system_prompt: str = Field(
        description="The optimized system prompt for the Target Agent. It must give clear instructions to solve the specific task based on the Judge's feedback."
    )

class JudgeEvaluation(BaseModel):
    is_correct: bool = Field(
        description="True if the actual output successfully fulfills the task and matches the expected output intent."
    )
    feedback: str = Field(
        description="Detailed explanation of why the output is correct or incorrect. If incorrect, explicitly state what the model did wrong."
    )