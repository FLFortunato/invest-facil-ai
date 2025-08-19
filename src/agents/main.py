from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages, StateGraph
from src.prompts.main_agent_prompt import MAIN_AGENT_PROMPT
from src.agents.stock_agent import stock_agent_run
from src.agents.currency_agent import currency_agent_run
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import START
import os

load_dotenv()


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


model = ChatOpenAI(model=os.getenv("MAIN_MODEL") or "")
tools = [stock_agent_run, currency_agent_run]

llm_with_tool = model.bind_tools(tools)


async def supervisor(state: State) -> State:
    sys_prompt = SystemMessage(content=MAIN_AGENT_PROMPT)
    response = await llm_with_tool.ainvoke([sys_prompt] + list(state["messages"]))

    return {"messages": [response]}


workflow = StateGraph(State)

workflow.add_node("supervisor", supervisor)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "supervisor")
workflow.add_conditional_edges("supervisor", tools_condition)
workflow.add_edge("tools", "supervisor")

supervisor_graph = workflow.compile()
