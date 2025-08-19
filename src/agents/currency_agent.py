from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from src.prompts.currency_agent_prompt import CURRENCY_AGENT_PROMPT
from src.tools.currency.tools import get_currencies_list
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


async def currency_agent_run(user_question: str):

    response = await currency_agent.ainvoke(
        {"messages": [HumanMessage(content=user_question)]}
    )

    return response["messages"][-1].content
