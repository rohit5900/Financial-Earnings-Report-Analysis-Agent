from .models import AgentFinding, Extraction
from .semantic_agent import SemanticAgent


class OutlookAnalyst(SemanticAgent):
    def __init__(self):
        super().__init__("Outlook Analyst", "Assess only forward guidance and outlook statements. Quote/cite supplied source IDs; do not extrapolate.")

    def analyze(self, data: Extraction) -> AgentFinding:
        ids = list(dict.fromkeys(data.metric("guidance").evidence_ids + data.outlook_evidence_ids))
        if self.uses_model:
            text = self.ask_sync(f"Assess forward guidance using only these excerpts and cite IDs.\n{data.evidence_text(ids)}")
            return AgentFinding(self.name, text, ids)
        statements = [data.evidence[sid].text for sid in ids if sid in data.evidence]
        return AgentFinding(self.name, " ".join(statements) if statements else "The report contains no extracted guidance statement.", ids)
