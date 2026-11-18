from dataclasses import dataclass, field


@dataclass(frozen=True)
class Evidence:
    source_id: str
    text: str


@dataclass
class Metric:
    name: str
    current: str | None = None
    previous: str | None = None
    guidance: str | None = None
    evidence_ids: list[str] = field(default_factory=list)


@dataclass
class Extraction:
    company: str = "Company"
    period: str = "Current quarter"
    metrics: dict[str, Metric] = field(default_factory=dict)
    evidence: dict[str, Evidence] = field(default_factory=dict)
    risk_evidence_ids: list[str] = field(default_factory=list)
    outlook_evidence_ids: list[str] = field(default_factory=list)
    header_evidence_ids: list[str] = field(default_factory=list)

    def evidence_text(self, ids: list[str]) -> str:
        return "\n".join(f"[{sid}] {self.evidence[sid].text}" for sid in ids if sid in self.evidence)

    def metric(self, name: str) -> Metric:
        return self.metrics.get(name, Metric(name=name))


@dataclass
class AgentFinding:
    agent: str
    text: str
    evidence_ids: list[str] = field(default_factory=list)
