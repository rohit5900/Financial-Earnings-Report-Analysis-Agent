"""Manager-led fan-out/fan-in workflow."""
from concurrent.futures import ThreadPoolExecutor
from .comparison_agent import ComparisonAgent
from .editor_manager import EditorManager
from .extraction_agent import ExtractionAgent
from .outlook_analyst import OutlookAnalyst
from .revenue_analyst import RevenueAnalyst
from .risk_analyst import RiskAnalyst


class EarningsDesk:
    def __init__(self):
        self.extractor = ExtractionAgent()
        self.analysts = [RevenueAnalyst(), RiskAnalyst(), OutlookAnalyst(), ComparisonAgent()]
        self.editor = EditorManager()

    def run(self, report_text: str) -> str:
        extracted = self.extractor.run(report_text)
        with ThreadPoolExecutor(max_workers=len(self.analysts)) as pool:
            findings = list(pool.map(lambda agent: agent.analyze(extracted), self.analysts))
        return self.editor.compile(extracted, findings)
import asyncio
