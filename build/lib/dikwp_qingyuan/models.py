from __future__ import annotations
from dataclasses import dataclass, asdict, field
from typing import Any

@dataclass(frozen=True)
class AnalysisInput:
    text: str
    purpose: str = "unspecified"
    audience: str = "general"
    source_type: str = "unknown"
    interface_cues: tuple[str, ...] = ()
    observed_outcomes: tuple[str, ...] = ()
    user_context: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class DimensionScores:
    evidence_integrity: float
    context_completeness: float
    manipulation_pressure: float
    addiction_pressure: float
    interest_opacity: float
    vulnerability_exploitation: float
    relational_externality: float
    pseudo_knowledge_risk: float
    corrigibility: float
    observed_harm: float

@dataclass(frozen=True)
class WorldHypothesis:
    name: str
    support: float
    rationale: tuple[str, ...]
    distinguishing_observation: str

@dataclass(frozen=True)
class AnalysisResult:
    version: str
    primary_class: str
    protected_expression: bool
    scores: DimensionScores
    worlds: tuple[WorldHypothesis, ...]
    detected_signals: tuple[str, ...]
    missing_context: tuple[str, ...]
    interventions: tuple[str, ...]
    corrected_variant: str
    claim_boundary: str
    automatic_external_action_authority: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
