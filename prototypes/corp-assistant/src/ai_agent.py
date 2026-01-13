from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import ModelRequest, SummarizationMiddleware, dynamic_prompt
from langchain.tools import ToolRuntime, tool
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.redis import AsyncRedisSaver
from pydantic import BaseModel, Field, PositiveInt

from . import rag
from .core.enums import UserRole
from .core.schemas import OutputDocumentExt
from .services import minutes_of_meetings
from .settings import PROMPTS_DIR, settings
from .utils import current_datetime


class Context(BaseModel):
    """Контекст работы корпоративного AI ассистента"""

    user_id: PositiveInt
    full_name: str
    user_role: UserRole


class State(AgentState):
    """Текущее состояние ассистента"""

    tg_file_ids: list[str]


class RAGSearchInput(BaseModel):
    """Описание входных аргументов для RAG-поиска"""

    search_query: str = Field(
        description="Запрос для поиска релевантных документов"
    )
    top_k: PositiveInt = Field(
        default=10, description="Количество извлекаемых документов"
    )


@tool(
    "search_in_knowledge_base",
    description="Выполняет поиск информации во внутренней базе знаний",
    args_schema=RAGSearchInput,
)
async def rag_search(search_query: str, top_k: int = 10) -> str:
    """Выполняет поиск информации во внутренней базе знаний"""

    documents = await rag.retrieve_documents(search_query, top_k=top_k)
    return "\n\n".join(documents)


class MinutesOfMeetingInput(BaseModel):
    """Входные параметры для составления протокола совещания"""

    output_document_ext: OutputDocumentExt = Field(
        description="Формат документа для составленного протокола",
        examples=["pdf", "md", "docx"]
    )


@tool(
    "draw_up_minutes_of_meeting",
    description="Составляет протокол совещания по аудио записи",
    args_schema=MinutesOfMeetingInput,
)
async def draw_up_minutes_of_meeting(
        runtime: ToolRuntime[Context, State], output_document_ext: OutputDocumentExt
) -> str:
    await minutes_of_meetings.create_task(
        user_id=runtime.context.user_id,
        tg_file_ids=runtime.state["tg_file_ids"],
        output_document_ext=output_document_ext,
    )
    return "Ваша аудио запись принята в работу"


model = ChatOpenAI(
    api_key=settings.yandexcloud.apikey,
    model=settings.yandexcloud.yandexgpt_rc,
    base_url=settings.yandexcloud.base_url,
    temperature=0.5,
    max_retries=3
)

# Шаблон системного промпта AI ассистента
system_prompt = (PROMPTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
# Промпт для суммаризации истории чата
summary_prompt = (PROMPTS_DIR / "summary_prompt.md").read_text(encoding="utf-8")


@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    """Динамический системный промпт с информацией о компании и пользователе"""

    return system_prompt.format(
        current_datetime=current_datetime(),
        assistant_name=settings.assistant.name,
        company_name=settings.assistant.company_name,
        company_website=settings.assistant.company_website,
        company_description=settings.assistant.company_description,
        full_name=request.runtime.context.full_name
    )


summarization_middleware = SummarizationMiddleware(
    model=ChatOpenAI(
        api_key=settings.yandexcloud.apikey,
        model=settings.yandexcloud.qwen3_235b,
        base_url=settings.yandexcloud.base_url,
        temperature=0.2,
        max_retries=3
    ),
    trigger=("tokens", 4000),
    keep=("messages", 20),
    summary_prompt=summary_prompt
)


async def call_agent(
        thread_id: str, human_text: str, context: Context, tg_file_ids: list[str]
) -> str:
    async with AsyncRedisSaver.from_conn_string(settings.redis.url) as checkpointer:
        checkpointer.setup()
        agent = create_agent(
            model=model,
            context_schema=Context,
            state_schema=State,
            tools=[rag_search, draw_up_minutes_of_meeting],
            middleware=[dynamic_system_prompt, summarization_middleware],
            checkpointer=checkpointer,
        )
        config = {"configurable": {"thread_id": thread_id}}
        result = await agent.ainvoke(
            {"messages": [("human", human_text)], "tg_file_ids": tg_file_ids},
            context=context, config=config
        )
    return result["messages"][-1].content
