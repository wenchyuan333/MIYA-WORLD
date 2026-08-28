import uuid
import traceback
from datetime import datetime
from tools.miya_gateway.registry import get_function
import json
from pathlib import Path

LOG_PATH = Path("memory/OPERATION-LOG.md")
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

def _log(entry: str):
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")

def invoke(name: str, args: dict, caller: str = "local"):
    record_id = str(uuid.uuid4())
    started = datetime.utcnow().isoformat()
    _log(f"{started} | {caller} | invoke | {name} | {record_id} | args={json.dumps(args, ensure_ascii=False)}")
    fnrec = get_function(name)
    if not fnrec:
        _log(f"{datetime.utcnow().isoformat()} | {caller} | error | {name} | {record_id} | not found")
        return {"id": record_id, "status": "error", "error": "function not found"}
    try:
        res = fnrec["fn"](**args)
        _log(f"{datetime.utcnow().isoformat()} | {caller} | success | {name} | {record_id} | result={str(res)[:500]}")
        return {"id": record_id, "status": "ok", "result": res}
    except Exception as e:
        tb = traceback.format_exc()
        _log(f"{datetime.utcnow().isoformat()} | {caller} | exception | {name} | {record_id} | {tb}")
        return {"id": record_id, "status": "error", "error": str(e)}
