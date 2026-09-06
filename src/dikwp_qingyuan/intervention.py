from __future__ import annotations

def plan_intervention(analysis: dict) -> dict:
    primary=analysis.get("primary_class","")
    scores=analysis.get("scores",{})
    local=[]; institutional=[]; prohibited=[]
    if analysis.get("protected_expression"):
        local += ["preserve expression", "show source context", "offer support if distress is present"]
    if scores.get("context_completeness",1)<0.6:
        local += ["display context completion card", "show omitted parties, conditions and exceptions"]
    if scores.get("manipulation_pressure",0)>=0.4:
        local += ["add share friction", "remove urgency cue", "require a cooling-off step"]
        institutional += ["reduce recommendation amplification pending review", "require sponsorship and targeting disclosure"]
    if scores.get("addiction_pressure",0)>=0.35:
        local += ["pause autoplay", "insert session break", "hide variable-reward signals by user choice"]
        institutional += ["measure session harm and disable default dark patterns"]
    if scores.get("pseudo_knowledge_risk",0)>=0.45:
        local += ["hold purchase decision", "request syllabus, sample, refund, independent outcomes and conflicts"]
        institutional += ["hold monetisation until minimum disclosure is met", "preserve appeal and correction"]
    if scores.get("observed_harm",0)>=0.55:
        institutional += ["notify affected users with a correction", "open a due-process repair case", "draft restitution and prevention measures"]
    prohibited=[
        "automatic political-viewpoint penalty",
        "person-level good/bad label",
        "automatic external deletion or sanction",
        "automatic financial penalty",
        "secret behavioural surveillance",
        "treating sadness, criticism, whistleblowing or bad news as harmful by default",
    ]
    return {"primary":primary,"local_actions":list(dict.fromkeys(local)),"institutional_actions":list(dict.fromkeys(institutional)),"prohibited_actions":prohibited}
