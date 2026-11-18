from .models import AgentFinding, Extraction
from .semantic_agent import SemanticAgent


class RevenueAnalyst(SemanticAgent):
    def __init__(self):
        super().__init__("Revenue Analyst", "Analyze reported revenue and growth using only provided metrics and evidence IDs. Cite every statement.")

    def analyze(self, data: Extraction) -> AgentFinding:
        m = data.metric("revenue")
        evidence = m.evidence_ids
        if self.uses_model:
            prompt = f"Analyze revenue and growth. Cite only source IDs shown. Metrics: {m}. Evidence: {data.evidence_text(evidence)}"
            text = self.ask_sync(prompt)
            return AgentFinding(self.name, text, evidence)
        if m.current and m.previous:
            prior = m.previous.split(" in ")[0].rstrip(".")
            text = f"Revenue was {m.current}; the prior-quarter figure was {prior}."
        else:
            text = f"Revenue was {m.current or 'not disclosed'}."
        return AgentFinding(self.name, text, evidence)
