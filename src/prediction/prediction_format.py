from dataclasses import dataclass, asdict
from typing import Dict, List

@dataclass
class PredictionAnswer:
    answer: str
    context: str
    document_id: str
    meta: Dict
    offset_end: int
    offset_end_in_doc: int
    offset_start: int
    offset_start_in_doc: int
    probability: float
    score: float

    def get_answer(self) -> str:
        return self.answer

@dataclass
class PredictionOutput:
    answers: List[PredictionAnswer]
    no_ans_gap: float
    question: str

    def __post_init__(self):
        self.answers = [PredictionAnswer(**ans) for ans in self.answers]

    def as_dict(self):
        return asdict(self)
