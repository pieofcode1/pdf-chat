import uuid
from pydantic import BaseModel, ValidationError, field_validator
from datetime import datetime
from typing import Annotated, Dict, List, Literal, Tuple, Optional

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


class MediaAssetInfo(BaseModel):
    id: str
    asset_name: str
    blob_video_key: str
    blob_audio_key: Optional[str] = None
    blob_video_url: str
    blob_audio_url: Optional[str] = None
    frame_offset: int
    frame_count: int
    duration: int
    total_frames: int
    audio_transcription: Optional[str] = None
    audio_summary: Optional[str] = None
    audio_summary_vector: Optional[List[float]] = None
    video_summary: Optional[str] = None
    video_summary_vector: Optional[List[float]] = None
    created_at: str = datetime.now().isoformat()



class VideoFrameSummary(BaseModel):
    id: str
    frame_id: int
    asset_name: str
    url: str
    summary: str = ''
    summary_vector: List = list()
    created_at: str = datetime.now().isoformat()

    @field_validator('summary_vector')
    def convert_tuple_to_list(cls, v):
        if isinstance(v, tuple):
            return list(v)
        return v


















