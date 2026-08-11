from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, json

@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id:str; tool_name:str; parameters:dict; result_digest:str; created_at:str

class EvidenceRegistry:
    def __init__(self): self._records=[]
    def register(self, tool_name, parameters, result):
        digest=hashlib.sha256(json.dumps(result,sort_keys=True,default=str).encode()).hexdigest()[:16]
        rec=EvidenceRecord(f"E{len(self._records)+1:04d}",tool_name,parameters,digest,datetime.now(timezone.utc).isoformat())
        self._records.append(rec); return rec
    def to_dicts(self): return [asdict(r) for r in self._records]
