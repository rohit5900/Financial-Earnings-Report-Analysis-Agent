"""Structured extractor for the standard earnings-brief format used by the demo."""
import re

from .evidence_store import EvidenceStore
from .models import Extraction, Metric
from .semantic_agent import SemanticAgent


class ExtractionAgent(SemanticAgent):
    def __init__(self):
        super().__init__("Extraction Agent", "Extract only figures and exact evidence from the supplied earnings report. Never infer missing values.")

    def run(self, text: str) -> Extraction:
        store = EvidenceStore(text)
        result = Extraction(evidence=store.items)
        company = re.search(r"Company:[ \t]*(.+)", text, re.I)
        period = re.search(r"Period:[ \t]*(.+)", text, re.I)
        result.company = company.group(1).strip() if company else "Company"
        result.period = period.group(1).strip() if period else "Current quarter"
        for label in ("Company", "Period"):
            for sid, evidence in result.evidence.items():
                if evidence.text.lower().startswith(label.lower() + ":"):
                    result.header_evidence_ids.append(sid)

        patterns = {
            "revenue": r"Revenue:[ \t]*(.+)",
            "net_income": r"Net income:[ \t]*(.+)",
            "operating_margin": r"Operating margin:[ \t]*(.+)",
            "guidance": r"Guidance:[ \t]*(.+)",
        }
        for name, pattern in patterns.items():
            match = re.search(pattern, text, re.I)
            if not match:
                continue
            line = match.group(0).strip()
            source_id = self._match_evidence(line, result.evidence)
            metric = Metric(name=name, evidence_ids=[source_id] if source_id else [])
            if name == "guidance":
                metric.guidance = match.group(1).strip()
            else:
                chunks = re.split(r";\s*", match.group(1))
                metric.current = chunks[0].strip()
                if len(chunks) > 1:
                    metric.previous = chunks[1].strip()
            result.metrics[name] = metric

        for item in store.search("risk", "headwind", "uncertain", "delay", "cost", "exposure", "declined", "lower"):
            result.risk_evidence_ids.append(item.source_id)
        for item in store.search("guidance", "expect", "forecast", "outlook", "target"):
            result.outlook_evidence_ids.append(item.source_id)
        return result

    @staticmethod
    def _match_evidence(line: str, evidence: dict) -> str | None:
        normalized = " ".join(line.split()).lower()
        for sid, item in evidence.items():
            if normalized in item.text.lower():
                return sid
        return None
