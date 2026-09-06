from __future__ import annotations
from typing import Iterable
from .models import AnalysisInput, DimensionScores, WorldHypothesis, AnalysisResult
from .rules import (
    ABSOLUTES,SOURCE_MARKERS,CORRECTION_MARKERS,MANIPULATION_MARKERS,ZERO_SUM_MARKERS,
    SALES_MARKERS,PSEUDO_KNOWLEDGE_MARKERS,VULNERABLE_AUDIENCE_MARKERS,
    PROTECTED_EXPRESSION_MARKERS,OBSERVED_HARM_MARKERS,ADDICTION_CUES,RELATIONAL_PARTIES
)
from .util import hits, clamp, norm
from .context_repair import repair_context

PROTECTED_PURPOSES={"criticism","whistleblowing","grief","distress","news","audit","research","求助","举报","批评","调查"}

def _score_hits(items: list[str], base: float, step: float, cap: float=1.0) -> float:
    return clamp(base + step*len(items), 0, cap)

def analyze_content(
    text: str,
    purpose: str = "unspecified",
    audience: str = "general",
    source_type: str = "unknown",
    interface_cues: Iterable[str] | None = None,
    observed_outcomes: Iterable[str] | None = None,
    user_context: dict | None = None,
) -> dict:
    inp=AnalysisInput(
        text=text or "", purpose=purpose or "unspecified", audience=audience or "general",
        source_type=source_type or "unknown", interface_cues=tuple(interface_cues or ()),
        observed_outcomes=tuple(observed_outcomes or ()), user_context=user_context or {}
    )
    t=norm(inp.text)
    absolute=hits(t,ABSOLUTES); sources=hits(t,SOURCE_MARKERS); corrections=hits(t,CORRECTION_MARKERS)
    manip=hits(t,MANIPULATION_MARKERS); zero=hits(t,ZERO_SUM_MARKERS); sales=hits(t,SALES_MARKERS)
    pseudo=hits(t,PSEUDO_KNOWLEDGE_MARKERS); vulnerable=hits(t+" "+norm(inp.audience),VULNERABLE_AUDIENCE_MARKERS)
    protected=hits(t,PROTECTED_EXPRESSION_MARKERS); observed=hits(" ".join(inp.observed_outcomes)+" "+t,OBSERVED_HARM_MARKERS)
    parties=hits(t,RELATIONAL_PARTIES)

    evidence=clamp(0.50 + 0.08*len(sources) + (0.10 if source_type in {"primary","official","direct_observation"} else 0)
                   -0.035*len(absolute) -0.07*len(pseudo))
    care_slogan = (("照顾自己" in t or "爱自己" in t or "self-care" in t or "care for yourself" in t)
                   and ("孩子" in t or "child" in t or "mother" in t or "妈妈" in t or "宝妈" in t))
    care_context_present = any(x in t for x in ("协商","安全","暴力","资源","预算","替代照护","negotiate","safety","violence","resource","budget","substitute care"))
    context_complete=clamp(0.62 + 0.07*len(corrections) + 0.04*min(len(parties),3)
                           -0.06*len(absolute) -0.07*len(zero) - (0.10 if sales and not sources else 0)
                           - (0.25 if care_slogan and not care_context_present else 0))
    manipulation=_score_hits(manip+zero,0.06,0.12)
    interest_opacity=clamp(0.08+0.11*len(sales)+(0.18 if sales and not any(k in t for k in ["sponsored","affiliate","广告","赞助","佣金"] ) else 0))
    vulnerability_exploitation=clamp(0.04+0.08*len(vulnerable)+0.09*len(manip)+(0.12 if vulnerable and sales else 0))
    relational=clamp(0.06+0.12*len(zero)+(0.05 if parties and absolute else 0)+(0.10 if "夫妻" in t or "spouse" in t or "partner" in t else 0))
    pseudo_risk=clamp(0.08+0.15*len(pseudo)+0.08*len(sales)-0.06*len(sources)-0.04*len(corrections))
    corrigibility=clamp(0.42+0.10*len(corrections)+0.05*len(sources)-0.06*len(absolute)-0.05*len(manip))
    addiction=0.04
    for cue in inp.interface_cues:
        addiction += ADDICTION_CUES.get(cue,0.08)
    if "keep scrolling" in t or "刷不停" in t or "连续打卡" in t or "streak" in t:
        addiction += 0.18
    addiction=clamp(addiction)
    harm=clamp(0.10*len(observed)+(0.15 if inp.observed_outcomes else 0))

    protected_expression = (purpose in PROTECTED_PURPOSES or bool(protected)) and manipulation < 0.45 and pseudo_risk < 0.45
    scores=DimensionScores(
        evidence_integrity=round(evidence,4), context_completeness=round(context_complete,4),
        manipulation_pressure=round(manipulation,4), addiction_pressure=round(addiction,4),
        interest_opacity=round(interest_opacity,4), vulnerability_exploitation=round(vulnerability_exploitation,4),
        relational_externality=round(relational,4), pseudo_knowledge_risk=round(pseudo_risk,4),
        corrigibility=round(corrigibility,4), observed_harm=round(harm,4)
    )

    signals=[]
    mapping=[("absolute_claim",absolute),("source_marker",sources),("correction_marker",corrections),
             ("manipulation",manip),("zero_sum",zero),("sales_funnel",sales),("pseudo_knowledge",pseudo),
             ("vulnerable_audience",vulnerable),("protected_expression",protected),("observed_harm",observed)]
    for label,items in mapping:
        for item in items: signals.append(f"{label}:{item}")
    for cue in inp.interface_cues: signals.append(f"interface:{cue}")

    repair=repair_context(inp.text,inp.audience)
    missing=tuple(repair["missing_context"]) if context_complete < 0.72 else ()
    interventions=[]
    candidates=[]
    if protected_expression:
        candidates.append((0,"PROTECTED_NEGATIVE_OR_CRITICAL_EXPRESSION"))
        interventions += ["L0_PROTECT_EXPRESSION", "PRESERVE_SOURCE_AND_CONTEXT"]
    if evidence < 0.48:
        candidates.append((1,"EVIDENCE_NEEDED")); interventions += ["L1_EVIDENCE_LABEL", "ASK_FOR_SOURCE_AND_FALSIFIER"]
    if context_complete < 0.58:
        candidates.append((2,"CONTEXT_REPAIR_REQUIRED")); interventions += ["L2_CONTEXT_COMPLETION_OVERLAY", "SHOW_OMITTED_PARTIES_AND_EXCEPTIONS"]
    if manipulation >= 0.42:
        candidates.append((3,"MANIPULATION_FRICTION_REQUIRED")); interventions += ["L3_SHARE_FRICTION", "COOLING_OFF_AND_IDENTITY_PRESSURE_WARNING"]
    if addiction >= 0.38:
        candidates.append((4,"ADDICTION_CIRCUIT_BREAKER")); interventions += ["L4_PAUSE_AUTOPLAY_AND_INFINITE_SCROLL", "USER_CONTROLLED_SESSION_BREAK"]
    if pseudo_risk >= 0.48 or (interest_opacity>=0.52 and evidence<0.55):
        candidates.append((5,"PSEUDO_KNOWLEDGE_COMMERCIAL_HOLD")); interventions += ["L5_HOLD_PURCHASE_OR_SHARE", "DISCLOSE_PRICE_REFUND_UPSELL_EVIDENCE"]
    if vulnerability_exploitation >= 0.48:
        candidates.append((5,"VULNERABLE_TARGET_PROTECTION")); interventions += ["L5_REMOVE_PERSONALISED_PRESSURE", "REQUIRE_PLAIN_LANGUAGE_AND_INDEPENDENT_REVIEW"]
    if relational >= 0.48:
        candidates.append((4,"RELATIONAL_ZERO_SUM_REPAIR")); interventions += ["RELATIONAL_BURDEN_MAP", "REVERSIBLE_TRIAL_AND_REVIEW_DATE"]
    if harm >= 0.55:
        candidates.append((6,"VERIFIED_HARM_REPAIR_PROCESS")); interventions += ["L6_DUE_PROCESS_REPAIR", "CORRECTION_REACH_AND_RESTITUTION_DRAFT"]
    if not candidates:
        candidates=[(0,"PASS_WITH_TRACEABLE_CONTEXT")]
        interventions += ["L0_ALLOW", "OPTIONAL_CONTEXT_CARD"]
    candidates.sort(key=lambda x:x[0],reverse=True)
    primary=candidates[0][1]

    malicious_support=clamp(0.12+0.30*manipulation+0.20*pseudo_risk+0.15*interest_opacity+0.12*vulnerability_exploitation)
    sincere_incomplete=clamp(0.18+0.35*(1-context_complete)+0.12*corrigibility-0.10*manipulation)
    truthful_uncomfortable=clamp(0.16+0.36*evidence+0.22*(1-manipulation)+(0.18 if protected_expression else 0)-0.10*pseudo_risk)
    commercial_persuasion=clamp(0.10+0.38*interest_opacity+0.16*sales.__len__())
    distress_signal=clamp(0.08+(0.35 if protected_expression and purpose in {"distress","grief","求助"} else 0)+0.12*len(protected))
    worlds=(
        WorldHypothesis("truthful_but_uncomfortable",round(truthful_uncomfortable,4),("evidence and criticism must not be suppressed",),"independent sources confirm the core claim"),
        WorldHypothesis("sincere_but_context_incomplete",round(sincere_incomplete,4),("partial insight with omitted conditions",),"author adds exceptions and burden allocation when asked"),
        WorldHypothesis("commercial_persuasion",round(commercial_persuasion,4),("sales or conversion incentives detected",),"full price, refund, conflicts and independent outcomes are disclosed"),
        WorldHypothesis("manipulative_or_addictive_mechanism",round(malicious_support,4),("identity pressure, zero-sum framing or addictive cues",),"message loses conversion power after pressure cues are removed"),
        WorldHypothesis("distress_or_help_signal",round(distress_signal,4),("negative language may be a request for support",),"speaker accepts support and does not seek to coerce others"),
    )
    repaired=repair["repaired_variants"][0] if repair["repaired_variants"] else inp.text
    result=AnalysisResult(
        version="27.0.0", primary_class=primary, protected_expression=protected_expression,
        scores=scores, worlds=worlds, detected_signals=tuple(dict.fromkeys(signals)),
        missing_context=missing, interventions=tuple(dict.fromkeys(interventions)),
        corrected_variant=repaired,
        claim_boundary="Heuristic research output. It evaluates observable content and interface mechanisms, not a person's total worth, inner intent, diagnosis or legal liability.",
    )
    return result.to_dict()
