from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from src.prompts.currency_agent_prompt import CURRENCY_AGENT_PROMPT
from src.tools.currency.tools import get_currencies_list
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


class ResponseType(BaseModel):
    answer: str


chat_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)


currency_agent = create_react_agent(
    model=chat_model,
    tools=[get_currencies_list],
    prompt=CURRENCY_AGENT_PROMPT,
    name="currency_agent",
)


async def currency_agent_run(user_question: str):
    print("===================CURRENCY AGENT====================", user_question)
    response = await currency_agent.ainvoke(
        {"messages": [HumanMessage(content=user_question)]}
    )

    return response["messages"][-1].content
