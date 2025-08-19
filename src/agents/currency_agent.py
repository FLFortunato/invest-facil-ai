from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from src.prompts.currency_agent_prompt import CURRENCY_AGENT_PROMPT
from src.tools.currency.tools import get_currencies_list
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()


class ResponseType(BaseModel):
    answer: str


currency_agent = create_react_agent(
    model="gpt-4.1",
    tools=[get_currencies_list],
    prompt=CURRENCY_AGENT_PROMPT,
    name="currency_agent",
)


@tool
async def currency_agent_run(user_question: str):
    """
    Runs the Currency Agent with the provided user question and returns its output.

    This tool sends the user's query as a `HumanMessage` to the `currency_agent`,
    which is configured with tools for retrieving currency-related data, such as
    the list of available currencies, exchange rates, or other relevant financial
    information, based on a domain-specific prompt. The agent may call its tools,
    process the results, and return a structured response containing synthesized
    currency-related information.

    Args:
        user_question (str): A natural language question or request about currencies
                             or exchange rates.

    Returns:
        dict: A dictionary with a single key "response", whose value is the full
              agent invocation result, including the conversation messages and
              any tool outputs generated during processing.
    """
    response = await currency_agent.ainvoke(
        {"messages": [HumanMessage(content=user_question)]}
    )

    return {"response": response}
