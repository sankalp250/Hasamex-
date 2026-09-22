from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TranscriptOut(BaseModel):
    id: str
    filename: str
    expert_name: str
    role: str
    market: str
    chunk_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Evidence(BaseModel):
    source_id: str
    expert: str
    market: str
    timestamp: str
    speaker: str
    quote: str


class ExpertGuideAnswer(BaseModel):
    transcript_id: str
    expert: str
    market: str
    role: str
    answer: str
    evidence: list[Evidence]


class GuideQuestionResult(BaseModel):
    question: str
    answers: list[ExpertGuideAnswer]


class GuideAnalysisOut(BaseModel):
    questions: list[GuideQuestionResult]


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)
    transcript_id: str | None = None


class AskResponse(BaseModel):
    answer: str
    evidence: list[Evidence]


class ThemeItem(BaseModel):
    name: str
    summary: str
    evidence: list[Evidence]


class DifferenceItem(BaseModel):
    topic: str
    summary: str
    evidence: list[Evidence]


class CrossAnalysisOut(BaseModel):
    themes: list[ThemeItem]
    differences: list[DifferenceItem]
    corpus_count: int
