"""Small Semantic Kernel adapter with a deterministic demo fallback."""
import os


class SemanticAgent:
    def __init__(self, name: str, instructions: str):
        self.name = name
        self.instructions = instructions
        self._service = None
        if os.getenv("EARNINGS_DESK_DEMO_MODE") == "1":
            return
        groq_key = os.getenv("GROQ_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        if groq_key or openai_key:
            try:
                from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

                if groq_key:
                    from openai import AsyncOpenAI

                    client = AsyncOpenAI(
                        api_key=groq_key,
                        base_url="https://api.groq.com/openai/v1",
                    )
                    service = OpenAIChatCompletion(
                        ai_model_id=os.getenv("GROQ_CHAT_MODEL", "openai/gpt-oss-20b"),
                        async_client=client,
                    )
                else:
                    service = OpenAIChatCompletion(
                        ai_model_id=os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
                        api_key=openai_key,
                    )
                self._service = service
            except (ImportError, TypeError, ValueError) as exc:
                raise RuntimeError(
                    "Semantic Kernel could not initialize its chat service "
                    f"({type(exc).__name__}: {exc}). Install project dependencies with `python -m pip install -e .`."
                ) from exc

    @property
    def uses_model(self) -> bool:
        return self._service is not None

    async def ask(self, task: str) -> str:
        if self._service is None:
            raise RuntimeError("No model configured; use the agent's local analysis method.")
        from semantic_kernel.connectors.ai.open_ai import OpenAIChatPromptExecutionSettings
        from semantic_kernel.contents.chat_history import ChatHistory

        history = ChatHistory()
        history.add_system_message(self.instructions)
        history.add_user_message(task)
        response = await self._service.get_chat_message_content(
            chat_history=history,
            settings=OpenAIChatPromptExecutionSettings(),
        )
        return str(response.content or "").strip()

    def ask_sync(self, task: str) -> str:
        import asyncio
        return asyncio.run(self.ask(task))
