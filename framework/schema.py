import uuid
from pydantic import BaseModel, ValidationError
from datetime import datetime
from typing import Annotated, Dict, List, Literal, Tuple


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    total_cost: float


class LLMResponse(BaseModel):
    user_prompt: str
    system_response: str | None = None
    usage: TokenUsage
    created_on: int = datetime.now().isoformat()


class LLMStepRun(BaseModel):
    batch_id: str
    category: str
    type: str
    group: str
    question: str
    answer: str
    docs: list[dict]
    ts: str


class BatchRun(BaseModel):
    id: str
    context: str
    index_name: str
    created_at: str = datetime.now().isoformat()


class StepRun(BaseModel):
    id: str
    batch_id: str
    context: str
    name: str
    category: str
    group: str
    question: str
    persona: dict
    answer: str
    charges: dict
    docs: list[dict]
    index_name: str
    created_at: str = datetime.now().isoformat()


class Questionnaire(BaseModel):
    id: str
    name: str
    category: str
    title: str
    description: str
    personas: list[dict]
    questions: list[dict]
    _ts: int
    _etag: str


class Answer(BaseModel):
    answer: str
    persona: str


class PersonaQnA(BaseModel):
    question: str
    answers: list[Answer]


class QnAGroup(BaseModel):
    group: str
    responses: list[PersonaQnA]


class QnASummary(BaseModel):
    id: str
    context: str
    name: str
    category: str
    title: str
    description: str
    questions: list[QnAGroup]


class ContextInfo(BaseModel):
    id: str
    document: str
    index_name: str
    vector_store: str
    _ts: int
    _etag: str
