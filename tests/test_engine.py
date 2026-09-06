import json, tempfile, unittest
from pathlib import Path
from dikwp_qingyuan.engine import analyze_content
from dikwp_qingyuan.context_repair import repair_context
from dikwp_qingyuan.knowledge_audit import audit_knowledge_offer
from dikwp_qingyuan.relationship import simulate_relational_effect
from dikwp_qingyuan.intervention import plan_intervention
from dikwp_qingyuan.receipts import append_receipt, verify_ledger

class EngineTests(unittest.TestCase):
    def test_version(self): self.assertEqual(analyze_content("hello")["version"],"27.0.0")
    def test_no_external_authority(self): self.assertEqual(analyze_content("hello")["automatic_external_action_authority"],0)
    def test_scores_range(self):
        for v in analyze_content("hello")["scores"].values(): self.assertGreaterEqual(v,0); self.assertLessEqual(v,1)
    def test_multi_world(self): self.assertGreaterEqual(len(analyze_content("hello")["worlds"]),2)
    def test_criticism_protected(self): self.assertTrue(analyze_content("批评该政策并提供审计证据",purpose="criticism")["protected_expression"])
    def test_whistleblowing_protected(self): self.assertTrue(analyze_content("举报污染，附监测数据和来源",purpose="whistleblowing")["protected_expression"])
    def test_grief_protected(self): self.assertTrue(analyze_content("我很悲伤，需要帮助",purpose="distress")["protected_expression"])
    def test_bad_news_not_automatically_harmful(self): self.assertNotEqual(analyze_content("事故通报：三人受伤，来源见报告",purpose="news")["primary_class"],"PSEUDO_KNOWLEDGE_COMMERCIAL_HOLD")
    def test_pseudo_course_hold(self): self.assertEqual(analyze_content("科学证明秘密方法100%改变命运，马上购买课程",purpose="sales")["primary_class"],"PSEUDO_KNOWLEDGE_COMMERCIAL_HOLD")
    def test_sales_opacity(self): self.assertGreater(analyze_content("最后机会，购买训练营",purpose="sales")["scores"]["interest_opacity"],0.3)
    def test_vulnerable_target(self): self.assertGreater(analyze_content("失业学生最后机会，马上付费加入",purpose="sales")["scores"]["vulnerability_exploitation"],0.2)
    def test_zero_sum(self): self.assertGreater(analyze_content("伴侣是敌人，婚姻就是博弈，谁妥协谁输")["scores"]["relational_externality"],0.4)
    def test_context_repair(self): self.assertIn("child safety",repair_context("女性要先照顾自己才能照顾孩子")["missing_context"][0])
    def test_context_repair_has_cn(self): self.assertIn("家庭共同责任",repair_context("女性要先照顾自己才能照顾孩子")["repaired_variants"][0])
    def test_balanced_care_lower_manipulation(self):
        a=analyze_content("照护者需要休息，但应保障孩子安全并与伴侣协商，存在暴力则先求助")
        self.assertLess(a["scores"]["manipulation_pressure"],0.3)
    def test_addiction_autoplay(self): self.assertGreater(analyze_content("content",interface_cues=["autoplay","infinite_scroll"])["scores"]["addiction_pressure"],0.3)
    def test_addiction_break_action(self): self.assertIn("L4_PAUSE_AUTOPLAY_AND_INFINITE_SCROLL",analyze_content("content",interface_cues=["autoplay","infinite_scroll"])["interventions"])
    def test_evidence_marker(self):
        self.assertGreater(analyze_content("根据研究数据和来源 https://example.org")["scores"]["evidence_integrity"],analyze_content("绝对唯一方法")["scores"]["evidence_integrity"])
    def test_correction_marker(self): self.assertGreater(analyze_content("这可能取决于条件，存在局限和反例")["scores"]["corrigibility"],0.5)
    def test_offer_missing_refund(self): self.assertEqual(audit_knowledge_offer("秘密课程，保证逆袭",999,"","",0)["decision"],"PSEUDO_KNOWLEDGE_COMMERCIAL_HOLD")
    def test_offer_disclosure_can_reduce_risk(self):
        low=audit_knowledge_offer("课程包含样例、局限、来源和反例",100,"7-day refund","verified instructor",3)
        self.assertLess(low["risk"],audit_knowledge_offer("秘密课程保证逆袭",100,"","",0)["risk"])
    def test_offer_no_payment_authority(self): self.assertEqual(audit_knowledge_offer("course",1)["automatic_payment_authority"],0)
    def test_relationship_high_drift(self): self.assertEqual(simulate_relational_effect(.9,.8,.6,.1,.1)["mode"],"HIGH_ZERO_SUM_DRIFT")
    def test_relationship_safety_exception(self): self.assertEqual(simulate_relational_effect(violence_or_coercion_context=True)["mode"],"SAFETY_FIRST_EXCEPTION")
    def test_intervention_prohibits_viewpoint_penalty(self): self.assertIn("automatic political-viewpoint penalty",plan_intervention(analyze_content("hello"))["prohibited_actions"])
    def test_intervention_prohibits_person_label(self): self.assertIn("person-level good/bad label",plan_intervention(analyze_content("hello"))["prohibited_actions"])
    def test_manipulation_share_friction(self): self.assertIn("L3_SHARE_FRICTION",analyze_content("如果你真的爱家人就马上证明你是觉醒者")["interventions"])
    def test_context_overlay(self): self.assertIn("L2_CONTEXT_COMPLETION_OVERLAY",analyze_content("唯一正确答案")["interventions"])
    def test_observed_harm_repair(self):
        r=analyze_content("内容",observed_outcomes=["财产损失","家庭冲突","延误治疗","骚扰","儿童受忽视"])
        self.assertEqual(r["primary_class"],"VERIFIED_HARM_REPAIR_PROCESS")
    def test_no_human_diagnosis_claim(self): self.assertIn("not a person's total worth",analyze_content("x")["claim_boundary"])
    def test_receipt_chain(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"r.jsonl"; append_receipt(p,"a",{"x":1}); append_receipt(p,"b",{"x":2})
            self.assertTrue(verify_ledger(p)["valid"]); self.assertEqual(verify_ledger(p)["records"],2)
    def test_receipt_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"r.jsonl"; append_receipt(p,"a",{"x":1})
            p.write_text(p.read_text().replace('"x": 1','"x": 9'),encoding="utf-8")
            self.assertFalse(verify_ledger(p)["valid"])
    def test_repaired_variant_present(self): self.assertTrue(analyze_content("女性要先照顾自己才能照顾孩子")["corrected_variant"])
    def test_signals_deduplicated(self):
        s=analyze_content("必须必须必须")["detected_signals"]; self.assertEqual(len(s),len(set(s)))
    def test_allow_benign(self): self.assertIn(analyze_content("今天下午三点开会，议程见附件")["primary_class"],["PASS_WITH_TRACEABLE_CONTEXT","EVIDENCE_NEEDED"])

if __name__=="__main__": unittest.main()
