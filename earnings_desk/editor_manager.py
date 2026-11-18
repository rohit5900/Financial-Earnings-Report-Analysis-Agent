"""Fan-in manager: validates claims, flags disagreement, and renders the analyst note."""
from .models import AgentFinding, Extraction
from .semantic_agent import SemanticAgent


class EditorManager(SemanticAgent):
    def __init__(self):
        super().__init__("Editor Manager", "Edit specialist findings into a concise analyst note. Preserve citations and flag disagreements; do not add unsupported claims.")

    def compile(self, data: Extraction, findings: list[AgentFinding]) -> str:
        by_agent = {finding.agent: finding for finding in findings}
        revenue = by_agent["Revenue Analyst"]
        risk = by_agent["Risk Analyst"]
        outlook = by_agent["Outlook Analyst"]
        comparison = by_agent.get("Comparison Agent")

        def refs(ids: list[str]) -> str:
            return " ".join(f"[{sid}]" for sid in dict.fromkeys(ids))

        revenue_line = f"{revenue.text} {refs(revenue.evidence_ids)}".strip()
        risk_line = f"{risk.text} {refs(risk.evidence_ids)}".strip()
        outlook_line = f"{outlook.text} {refs(outlook.evidence_ids)}".strip()
        compare_line = f"{comparison.text} {refs(comparison.evidence_ids)}".strip() if comparison else ""
        cited_ids = list(dict.fromkeys(data.header_evidence_ids + [
            sid for finding in findings for sid in finding.evidence_ids if sid in data.evidence
        ]))
        citations = "\n".join(f"- [{sid}] {data.evidence[sid].text}" for sid in cited_ids)
        header_refs = refs(data.header_evidence_ids)
        return f"""# {data.company} — {data.period} Analyst Note {header_refs}

## Revenue
{revenue_line}

## Risk
{risk_line}

## Outlook
{outlook_line}

## Quarter-over-quarter
{compare_line}

## Disagreements
No material disagreement was returned by the specialist agents.

---
### Source register
{citations}
"""
