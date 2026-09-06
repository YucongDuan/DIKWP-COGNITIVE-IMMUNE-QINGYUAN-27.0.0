from __future__ import annotations
import json, hashlib, datetime
from pathlib import Path
from .util import canonical_json

def _hash(payload: dict, previous_hash: str) -> str:
    return hashlib.sha256((canonical_json(payload)+previous_hash).encode("utf-8")).hexdigest()

def append_receipt(path: str | Path, event_type: str, payload: dict) -> dict:
    p=Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    previous="0"*64
    if p.exists():
        lines=[x for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
        if lines:
            previous=json.loads(lines[-1])["hash"]
    body={
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload,
        "previous_hash": previous,
    }
    body["hash"]=_hash({k:v for k,v in body.items() if k!="hash"}, previous)
    with p.open("a",encoding="utf-8") as f:
        f.write(json.dumps(body,ensure_ascii=False,sort_keys=True)+"\n")
    return body

def verify_ledger(path: str | Path) -> dict:
    p=Path(path)
    if not p.exists():
        return {"valid":False,"records":0,"error":"missing"}
    prev="0"*64
    count=0
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip(): continue
        rec=json.loads(line)
        if rec.get("previous_hash")!=prev:
            return {"valid":False,"records":count,"error":"previous_hash_mismatch"}
        expected=_hash({k:v for k,v in rec.items() if k!="hash"}, prev)
        if rec.get("hash")!=expected:
            return {"valid":False,"records":count,"error":"hash_mismatch"}
        prev=rec["hash"]
        count+=1
    return {"valid":True,"records":count,"head":prev}
