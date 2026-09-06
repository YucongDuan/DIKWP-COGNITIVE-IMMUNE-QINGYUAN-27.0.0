from __future__ import annotations
from .util import clamp

def simulate_relational_effect(
    unilateral_burden_shift: float = 0.0,
    contempt_or_demonisation: float = 0.0,
    child_or_dependent_risk: float = 0.0,
    negotiation_quality: float = 0.5,
    resource_support: float = 0.5,
    violence_or_coercion_context: bool = False,
) -> dict:
    if violence_or_coercion_context:
        return {
            "mode": "SAFETY_FIRST_EXCEPTION",
            "zero_sum_drift": 0.0,
            "recommendation": "Prioritise immediate safety, professional support and protected decision-making; ordinary relationship compromise is not the first intervention.",
            "recommendation_cn": "优先保障即时安全、专业支持与受保护的决策空间；一般性的关系妥协不是首要干预。",
        }
    drift = clamp(
        0.38*unilateral_burden_shift + 0.30*contempt_or_demonisation + 0.22*child_or_dependent_risk
        - 0.18*negotiation_quality - 0.12*resource_support + 0.18
    )
    mode = "HIGH_ZERO_SUM_DRIFT" if drift >= 0.62 else "REPAIRABLE_TENSION" if drift >= 0.35 else "COOPERATIVE_RANGE"
    return {
        "mode": mode,
        "zero_sum_drift": round(drift,4),
        "recommendation": "Make burdens, beneficiaries, constraints and review dates explicit; negotiate a reversible trial instead of turning a partial principle into an identity battle.",
        "recommendation_cn": "显式列出负担、受益者、约束和复盘日期；用可撤销的小范围试行替代把局部原则升级为身份战争。",
    }
