from __future__ import annotations
from .util import norm

CAREGIVING_REPAIR_CN = (
    "照护者的休息、健康与安全是家庭共同责任，但自我照顾不应被解释为把孩子的基本照护、风险或全部家务单边转移给另一方。"
    "应先明确孩子的安全与发展需要，再由伴侣、家庭成员或社会支持共同协商时间、劳动、预算和替代照护；"
    "若存在暴力、强迫控制、严重抑郁、单亲无支持或紧急健康风险，应优先寻求专业与公共支持，而不是用一句口号处理复杂处境。"
)
CAREGIVING_REPAIR_EN = (
    "A caregiver's rest, health and safety are a shared family responsibility, but self-care should not be interpreted as transferring a child's essential care, risk, or all domestic work unilaterally to another person. "
    "First protect the child's safety and developmental needs, then negotiate time, labour, budget and substitute care among partners, family members or public support. "
    "Where violence, coercive control, severe depression, unsupported single parenting or urgent health risk is present, professional and public support should take priority over a slogan."
)

def repair_context(text: str, audience: str = "general") -> dict:
    t = norm(text)
    missing = []
    repair = []
    if (("照顾自己" in t or "爱自己" in t or "self-care" in t or "care for yourself" in t)
        and ("孩子" in t or "child" in t or "mother" in t or "妈妈" in t or "宝妈" in t)):
        missing = [
            "child safety and developmental needs / 孩子的安全与发展需要",
            "partner and household burden distribution / 伴侣与家庭负担分配",
            "time, income and substitute-care constraints / 时间、收入与替代照护约束",
            "exceptions involving violence, coercion or urgent health risk / 暴力、控制与紧急健康风险例外",
            "a concrete negotiation and review mechanism / 可执行的协商与复盘机制",
        ]
        repair = [CAREGIVING_REPAIR_CN, CAREGIVING_REPAIR_EN]
        core = "Caregiver sustainability is a legitimate concern, but the slogan is not a complete decision rule. / 照护者可持续性是合理核心，但口号不是完整决策规则。"
        risk = "A one-sided reading can convert care into identity conflict, unilateral burden transfer or a commercial awakening narrative. / 片面理解可能把照护议题转化为身份对抗、单边负担转移或商业化觉醒叙事。"
    else:
        missing = [
            "who is affected and who bears the burden / 谁受到影响、谁承担负担",
            "scope, conditions and exceptions / 适用范围、条件与例外",
            "source and evidence level / 来源与证据层级",
            "conflicts of interest and sales incentives / 利益冲突与售卖动机",
            "how the claim can be corrected or falsified / 如何更正或证伪",
        ]
        repair = [
            "Rewrite the claim as a conditional statement: identify the beneficiary, affected parties, evidence, exceptions, burden allocation and a review point.",
            "将断言改写为条件命题：明确受益者、受影响主体、证据、例外、负担分配和复盘节点。",
        ]
        core = "The statement may contain a useful partial insight, but it does not yet constitute a complete action rule. / 该表述可能包含局部合理洞见，但尚不能构成完整行动规则。"
        risk = "Without context, a partial truth can be used as a universal prescription or sales hook. / 缺乏语境时，局部真理可能被包装成普遍处方或销售钩子。"
    return {
        "original": text,
        "audience": audience,
        "reasonable_core": core,
        "missing_context": missing,
        "misreading_risk": risk,
        "repaired_variants": repair,
    }
