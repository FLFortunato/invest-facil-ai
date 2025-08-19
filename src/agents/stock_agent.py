from dotenv import load_dotenv
from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from src.prompts.stock_agent_prompt import STOCK_AGENT_PROMPT
from src.tools.stock.stock_tools import (
    search_stock_updated_data,
    search_stock_aggregated_data,
)
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()


class ResponseType(BaseModel):
    answer: str


stock_agent = create_react_agent(
    model="gpt-4.1",
    tools=[search_stock_updated_data, search_stock_aggregated_data],
    prompt=STOCK_AGENT_PROMPT,
    name="stock_agent",
)


async def stock_agent_run(user_question: str):
    """
    Runs the Stock Agent with the provided user question and returns its output.

    This tool sends the user's query as a `HumanMessage` to the `stock_agent`,
    which is configured with tools for retrieving updated and aggregated stock data
    based on a domain-specific prompt. The agent may call its tools, process the
    results, and return a structured response containing synthesized stock-related
    information.

    Args:
        user_question (str): A natural language question or request about stocks.

    Returns:
        dict: A dictionary with a single key "response", whose value is the full
              agent invocation result, including the conversation messages and
              any tool outputs generated during processing.
    """
    response = await stock_agent.ainvoke(
        {"messages": [HumanMessage(content=user_question)]}
    )

    return response["messages"][-1].content
