from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from .engine import analyze_content
from .context_repair import repair_context
from .knowledge_audit import audit_knowledge_offer
from .relationship import simulate_relational_effect
from .intervention import plan_intervention
from .receipts import append_receipt, verify_ledger

DEMO_TEXT="女性要先好好照顾自己才能照顾孩子。真正觉醒的女人不能向家庭妥协，马上加入训练营。"

def dump(value, out=None):
    text=json.dumps(value,ensure_ascii=False,indent=2)
    if out:
        Path(out).write_text(text,encoding="utf-8")
    else:
        print(text)

def main(argv=None):
    p=argparse.ArgumentParser(prog="qingyuan27",description="DIKWP QINGYUAN 27.0")
    sp=p.add_subparsers(dest="cmd",required=True)
    a=sp.add_parser("analyze"); a.add_argument("text",nargs="?"); a.add_argument("--file"); a.add_argument("--purpose",default="unspecified"); a.add_argument("--audience",default="general"); a.add_argument("--cue",action="append",default=[]); a.add_argument("--out")
    r=sp.add_parser("repair-context"); r.add_argument("text"); r.add_argument("--out")
    k=sp.add_parser("audit-offer"); k.add_argument("text"); k.add_argument("--price",type=float,default=0); k.add_argument("--refund",default=""); k.add_argument("--credentials",default=""); k.add_argument("--links",type=int,default=0); k.add_argument("--out")
    s=sp.add_parser("simulate-relation"); s.add_argument("--burden",type=float,default=.5); s.add_argument("--contempt",type=float,default=.4); s.add_argument("--dependent-risk",type=float,default=.4); s.add_argument("--negotiation",type=float,default=.3); s.add_argument("--support",type=float,default=.3); s.add_argument("--violence",action="store_true"); s.add_argument("--out")
    d=sp.add_parser("demo"); d.add_argument("--workspace",default="outputs/demo")
    v=sp.add_parser("verify-ledger"); v.add_argument("path")
    args=p.parse_args(argv)
    if args.cmd=="analyze":
        text=args.text or (Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read())
        res=analyze_content(text,purpose=args.purpose,audience=args.audience,interface_cues=args.cue)
        res["intervention_plan"]=plan_intervention(res); dump(res,args.out)
    elif args.cmd=="repair-context": dump(repair_context(args.text),args.out)
    elif args.cmd=="audit-offer": dump(audit_knowledge_offer(args.text,args.price,args.refund,args.credentials,args.links),args.out)
    elif args.cmd=="simulate-relation": dump(simulate_relational_effect(args.burden,args.contempt,args.dependent_risk,args.negotiation,args.support,args.violence),args.out)
    elif args.cmd=="verify-ledger": dump(verify_ledger(args.path))
    elif args.cmd=="demo":
        ws=Path(args.workspace); ws.mkdir(parents=True,exist_ok=True)
        result=analyze_content(DEMO_TEXT,purpose="education",audience="caregivers",interface_cues=["autoplay","infinite_scroll","outrage_loop"])
        result["context_repair"]=repair_context(DEMO_TEXT,"caregivers")
        result["offer_audit"]=audit_knowledge_offer(DEMO_TEXT,1999,"","self-claimed",0)
        result["relationship_simulation"]=simulate_relational_effect(.8,.7,.5,.2,.2)
        result["intervention_plan"]=plan_intervention(result)
        dump(result,ws/"demo_analysis.json")
        ledger=ws/"receipts.jsonl"
        if ledger.exists(): ledger.unlink()
        append_receipt(ledger,"content_analysis",{"primary":result["primary_class"]})
        append_receipt(ledger,"context_repair",{"missing":result["missing_context"]})
        append_receipt(ledger,"intervention_plan",result["intervention_plan"])
        dump(verify_ledger(ledger),ws/"ledger_verification.json")
        print(str(ws.resolve()))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
