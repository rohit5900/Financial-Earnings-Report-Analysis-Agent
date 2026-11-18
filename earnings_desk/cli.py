import argparse
from pathlib import Path

from .orchestrator import EarningsDesk


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a grounded earnings analyst note")
    parser.add_argument("report", help="Path to a UTF-8 earnings report text file")
    parser.add_argument("-o", "--output", default="analyst_note.md", help="Output Markdown file")
    args = parser.parse_args()
    report_text = Path(args.report).read_text(encoding="utf-8")
    note = EarningsDesk().run(report_text)
    Path(args.output).write_text(note, encoding="utf-8")
    print(f"Wrote analyst note: {args.output}")


if __name__ == "__main__":
    main()
