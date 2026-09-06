from __future__ import annotations
from .rules import SALES_MARKERS, PSEUDO_KNOWLEDGE_MARKERS, SOURCE_MARKERS, CORRECTION_MARKERS
from .util import hits, clamp, norm

def audit_knowledge_offer(text: str, price: float = 0.0, refund_terms: str = "", credentials: str = "", evidence_links: int = 0) -> dict:
    t = norm(text)
    sales = hits(t, SALES_MARKERS)
    pseudo = hits(t, PSEUDO_KNOWLEDGE_MARKERS)
    sources = hits(t, SOURCE_MARKERS)
    caveats = hits(t, CORRECTION_MARKERS)
    opacity = 0.18 + 0.10*len(sales) + (0.20 if price > 0 and not refund_terms.strip() else 0) + (0.12 if price > 0 and not credentials.strip() else 0)
    evidence_gap = 0.55 + 0.12*len(pseudo) - 0.10*len(sources) - 0.06*evidence_links - 0.06*len(caveats)
    risk = clamp(0.45*opacity + 0.55*evidence_gap)
    hold = risk >= 0.55
    checks = [
        "Declare the seller, price, refund and upsell chain.",
        "Separate testimonials from independent outcome evidence.",
        "List what the material cannot establish and who should not use it.",
        "Provide a sample, syllabus, measurable learning outcome and correction channel.",
        "Disclose affiliate, sponsorship, referral and data-use interests.",
    ]
    return {
        "risk": round(risk, 4),
        "decision": "PSEUDO_KNOWLEDGE_COMMERCIAL_HOLD" if hold else "ALLOW_WITH_DISCLOSURE_AND_EVIDENCE",
        "sales_signals": sales,
        "pseudo_knowledge_signals": pseudo,
        "source_signals": sources,
        "correction_signals": caveats,
        "required_checks": checks,
        "automatic_payment_authority": 0,
    }
