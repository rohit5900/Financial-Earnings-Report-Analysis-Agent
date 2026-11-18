from .models import AgentFinding, Extraction
from .semantic_agent import SemanticAgent


class RiskAnalyst(SemanticAgent):
    def __init__(self):
        super().__init__("Risk Analyst", "Identify risks and red flags only from supplied report excerpts. Cite every finding; do not invent risks.")

    def analyze(self, data: Extraction) -> AgentFinding:
        ids = data.risk_evidence_ids
        if self.uses_model:
            text = self.ask_sync(f"Identify report risks. Cite only these source IDs.\n{data.evidence_text(ids)}")
            return AgentFinding(self.name, text, ids)
        meaningful = [sid for sid in ids if any(x in data.evidence[sid].text.lower() for x in ("risk", "headwind", "delay", "uncertain", "exposure"))]
        if not meaningful:
            return AgentFinding(self.name, "No explicit risk statement was found in the report text.", [])
        excerpts = [data.evidence[sid].text for sid in meaningful]
        return AgentFinding(self.name, " ".join(excerpts), meaningful)
