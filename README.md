# Financial Earnings Report Analysis Desk

A manager-led, fan-out/fan-in workflow that turns a text earnings report into a concise analyst note with traceable report evidence.

## Agents

- **Extraction Agent** parses revenue, net income, operating margin, guidance, and source passages into shared structured memory.
- **Revenue Analyst** summarizes the revenue result and growth.
- **Risk Analyst** identifies explicit risks and red flags from the report text.
- **Outlook Analyst** assesses forward guidance.
- **Comparison Agent** (group-of-three extension) reports quarter-over-quarter direction where figures are available.
- **Editor Manager** gathers specialist findings and assembles the final note with a source register.

## Run the demonstration

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
earnings-desk sample_earnings_report.txt -o analyst_note.md
```

## Use the upload interface

```powershell
python -m pip install -e .
streamlit run app.py
```

Open the local address printed in the terminal. Upload a text-based PDF, `.xlsx`, or `.xls` earnings report, then select **Generate analyst note**. Review the extracted-text preview before analysis and download the finished Markdown note from the page. Scanned image-only PDFs need OCR before upload. The sidebar accepts a Groq key for model-backed analysis; select **Find models available to my key** to load models returned for that key, then choose one from the list. This checks Groq's model list endpoint and does not run an inference request. Leave the key empty for deterministic demo mode.

The workflow runs without credentials in deterministic demo mode. To use your Groq account, set `GROQ_API_KEY` in the environment; optionally set `GROQ_CHAT_MODEL` (default: `openai/gpt-oss-20b`). Each specialist uses a Semantic Kernel OpenAI chat-completion service connected to Groq's OpenAI-compatible chat endpoint. If both Groq and OpenAI keys are configured, Groq is selected. OpenAI remains available with `OPENAI_API_KEY` and `OPENAI_CHAT_MODEL`. Each agent keeps its role and input scope; specialists receive extracted figures and cited report passages. Groq model access varies by account; choose a model enabled for your key.

In PowerShell, set the key for the current terminal session with `$env:GROQ_API_KEY = "your-key"` before running the command. Keep the actual key in your local environment and out of the report, source files, and chat messages.

## Coordination and grounding

The extraction agent creates source IDs for report sentences and stores them in a shared evidence map. The manager passes the same extracted memory to each specialist (fan-out), gathers their findings (fan-in), and the editor emits citations such as `[S04]` plus the matching source register. The sample format uses explicit `Revenue`, `Net income`, `Operating margin`, and `Guidance` lines; adapting the extraction rules is expected when a filing uses different labels or table layouts.

## Input and output

Input is a UTF-8 `.txt` earnings report. Output is a Markdown analyst note with Revenue, Risk, Outlook, quarter-over-quarter comparison, disagreement status, and cited source passages. The included sample demonstrates every workflow stage.
