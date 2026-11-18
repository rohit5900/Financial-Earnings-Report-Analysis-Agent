"""Local browser interface for the Financial Earnings Report Analysis Desk."""
import os

import streamlit as st

from earnings_desk.document_loader import DocumentReadError, extract_document_text
from earnings_desk.orchestrator import EarningsDesk


st.set_page_config(page_title="Financial Earnings Analysis Desk", page_icon="📊", layout="wide")
st.title("Financial Earnings Report Analysis Desk")
st.caption("Upload an earnings report and generate a sourced analyst note.")


def clear_groq_models() -> None:
    st.session_state.pop("groq_available_models", None)


with st.sidebar:
    st.subheader("Model settings")
    groq_key = st.text_input(
        "Groq API key (optional)",
        type="password",
        on_change=clear_groq_models,
        help="Used only for this local app session. Leave blank to use deterministic demo mode.",
    )
    if st.button("Find models available to my key", disabled=not groq_key.strip()):
        try:
            from openai import OpenAI

            groq_client = OpenAI(
                api_key=groq_key.strip(),
                base_url="https://api.groq.com/openai/v1",
            )
            accessible = sorted(model.id for model in groq_client.models.list().data)
            if accessible:
                st.session_state["groq_available_models"] = accessible
                st.success(f"Found {len(accessible)} models available to this key.")
            else:
                st.session_state["groq_available_models"] = []
                st.warning("Groq returned no models for this key.")
        except Exception:
            st.error("Could not retrieve models. Check the Groq key and try again.")

    accessible_models = st.session_state.get("groq_available_models", [])
    if accessible_models:
        preferred = "openai/gpt-oss-20b"
        default_index = accessible_models.index(preferred) if preferred in accessible_models else 0
        groq_model = st.selectbox("Groq model", accessible_models, index=default_index)
    else:
        groq_model = st.text_input("Groq model", value="openai/gpt-oss-20b")
    st.caption("Your key is not written to the project files.")

uploaded = st.file_uploader(
    "Choose an earnings report",
    type=["pdf", "xlsx", "xls"],
    help="Text-based PDFs and Excel workbooks are supported. Scanned PDFs need OCR first.",
)

if uploaded is None:
    st.info("Upload a PDF or Excel report to begin.")
else:
    upload_token = f"{uploaded.name}:{uploaded.size}"
    if st.session_state.get("upload_token") != upload_token:
        st.session_state["upload_token"] = upload_token
        st.session_state.pop("earnings_note", None)
        st.session_state.pop("earnings_filename", None)
    try:
        report_text = extract_document_text(uploaded.name, uploaded.getvalue())
    except DocumentReadError as exc:
        st.error(str(exc))
    else:
        st.success(f"Read {uploaded.name} · {len(report_text):,} characters extracted")
        with st.expander("Preview extracted report text"):
            st.text_area("Extracted text", report_text[:12000], height=240, label_visibility="collapsed")
            if len(report_text) > 12000:
                st.caption("Preview clipped at 12,000 characters. The full extracted text is used for analysis.")

        if st.button("Generate analyst note", type="primary", disabled=not report_text.strip()):
            if groq_key.strip():
                os.environ["GROQ_API_KEY"] = groq_key.strip()
                os.environ["GROQ_CHAT_MODEL"] = groq_model.strip() or "openai/gpt-oss-20b"
                os.environ.pop("EARNINGS_DESK_DEMO_MODE", None)
            else:
                os.environ.pop("GROQ_API_KEY", None)
                os.environ["EARNINGS_DESK_DEMO_MODE"] = "1"
            try:
                with st.spinner("The analysis team is reviewing the report…"):
                    note = EarningsDesk().run(report_text)
                st.session_state["earnings_note"] = note
                st.session_state["earnings_filename"] = uploaded.name
            except Exception as exc:
                detail = str(exc)
                if "model_not_found" in detail or "does not exist or you do not have access" in detail:
                    st.error(
                        "Groq does not allow this key to use the selected model. "
                        "Choose a model your key can access. The default is now openai/gpt-oss-20b."
                    )
                else:
                    st.error(f"The note could not be generated. Check the report format and model settings. Details: {detail}")

if st.session_state.get("earnings_note"):
    st.divider()
    st.subheader("Analyst note")
    st.markdown(st.session_state["earnings_note"])
    base_name = os.path.splitext(st.session_state.get("earnings_filename", "earnings_report"))[0]
    st.download_button(
        "Download analyst note",
        data=st.session_state["earnings_note"],
        file_name=f"{base_name}_analyst_note.md",
        mime="text/markdown",
        type="secondary",
    )
