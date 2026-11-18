from .models import AgentFinding, Extraction
from .semantic_agent import SemanticAgent


class ComparisonAgent(SemanticAgent):
    def __init__(self):
        super().__init__("Comparison Agent", "Compare current-quarter figures to the previous quarter, reporting direction only. Cite the source IDs.")

    def analyze(self, data: Extraction) -> AgentFinding:
        metrics = [data.metric(k) for k in ("revenue", "net_income", "operating_margin")]
        cited = [sid for metric in metrics for sid in metric.evidence_ids]
        if self.uses_model:
            prompt = f"Compare each available metric with prior quarter; report up/down/flat only where possible. Cite source IDs.\n{data.evidence_text(cited)}"
            return AgentFinding(self.name, self.ask_sync(prompt), cited)
        labels = {"revenue": "Revenue", "net_income": "Net income", "operating_margin": "Operating margin"}
        changes = []
        for m in metrics:
            if m.current and m.previous:
                a, b = self._number(m.current), self._number(m.previous)
                direction = "up" if a > b else "down" if a < b else "flat"
                current = m.current.rstrip(".")
                previous = m.previous.rstrip(".")
                if m.name == "revenue":
                    previous = previous.split(" in ")[0]
                    changes.append(f"{labels[m.name]} {direction} (from {previous} to {current.split(',')[0]})")
                else:
                    changes.append(f"{labels[m.name]} {direction} (from {previous.split(' in ')[0]} to {current})")
        return AgentFinding(self.name, "; ".join(changes) if changes else "Prior-quarter comparisons are not available.", cited)

    @staticmethod
    def _number(value: str) -> float:
        import re
        match = re.search(r"-?[\d,.]+", value)
        return float(match.group(0).replace(",", "")) if match else 0.0
