from typing import Annotated, Literal, TypedDict

import logging
import operator
from uuid import UUID

from langchain.messages import AnyMessage, SystemMessage, ToolMessage
from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from .dependencies import customers_db, workspaces_db, yandexgpt_pro

logger = logging.getLogger(__name__)

# Определение инструментов агента


@tool
def get_workspace_by_user(user_id: UUID) -> dict[str, str] | None:
    """Получает информацию о рабочем пространстве пользователя,
    такую как название компании, описание и тип организации.

    Attributes:
        user_id: Идентификатор пользователя.
    """

    for row in workspaces_db:
        if row["user_id"] == user_id:
            return row.get("workspace")
    return None


@tool
def save_customer_info(user_id: UUID, useful_note: str) -> None:
    """Сохраняет информацию о клиенте.

    Attributes:
        user_id: Идентификатор пользователя.
        useful_note: Полезная информация о клиенте полученная из его ответов"""

    for row in customers_db:
        if row["user_id"] == user_id:
            row["customer_info"].append(useful_note)
            return
    customers_db.append({"user_id": user_id, "customer_info": [useful_note]})
    logger.info("Saved info about customer: '%s'", useful_note)


@tool
def get_current_customer_info(user_id: UUID) -> str:
    """Получает текущую собранную информацию о клиенте.

    Attributes:
        user_id: Идентификатор пользователя.
    """

    for row in customers_db:
        if row["user_id"] == user_id:
            return "\n".join(row["customer_info"])
    return "Информация пока не добавлена"


@tool
def finalize_interview(user_id: UUID, final_note: str | None = None) -> str:
    """Завершение опроса и передаче данных на следующий этап.
    После вызовы этого инструмента поблагодари пользователя за ответы.

    Attributes:
        user_id: Идентификатор пользователя.
        final_note: Любые дополнительные комментарии,
        которые будут добавлены в портрет клиента.
    """

    logger.info("Finalizing interview")
    if final_note is not None:
        for row in customers_db:
            if row["user_id"] == user_id:
                row["customer_info"].append(final_note)
                return "\n".join(row["customer_info"])
    for row in customers_db:
        if row["user_id"] == user_id:
            return "\n".join(row["customer_info"])
    return "Информация не была добавлена"


# Набор доступных инструментов
tools = [save_customer_info, get_current_customer_info, finalize_interview]
tools_by_names = {tool.name: tool for tool in tools}
llm_with_tools = yandexgpt_pro.bind_tools(tools)

# Определение состояния агента


class BriefingState(TypedDict):
    user_id: UUID
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int


# Определение узлов графа для построения ReAct агента


def llm_call(state: BriefingState) -> BriefingState:
    """Узел для вызова LLM"""

    system_text = f"""{...}
    **ИДЕНТИФИКАТОР ПОЛЬЗОВАТЕЛЯ:** {state["user_id"]}
    """
    return {
        "user_id": state["user_id"],
        "messages": [
            llm_with_tools.invoke(
                [SystemMessage(content=system_text)] + state["messages"]
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


def tool_node(state: BriefingState) -> dict[str, list[ToolMessage]]:
    """Узел для вызова инструмента"""

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_names[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


def should_continue(state: BriefingState) -> Literal["tool_node", END]:
    """Принимает решение о вызове инструмента или отдаче ответа пользователю"""

    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tool_node"
    return END


# Определение workflow агента

builder = StateGraph(BriefingState)

builder.add_node("llm_call", llm_call)
builder.add_node("tool_node", tool_node)

builder.add_edge(START, "llm_call")
builder.add_conditional_edges(
    "llm_call",
    should_continue,
    ["tool_node", END]
)
builder.add_edge("tool_node", "llm_call")

checkpointer = InMemorySaver()

briefing_agent = builder.compile(checkpointer=checkpointer)
