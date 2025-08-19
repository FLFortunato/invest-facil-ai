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
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


chat_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)


stock_agent = create_react_agent(
    model=chat_model,
    tools=[search_stock_updated_data, search_stock_aggregated_data],
    prompt=STOCK_AGENT_PROMPT,
    name="stock_agent",
)


async def stock_agent_run(user_question: str):
    print("===================STOCK AGENT====================", user_question)
    response = await stock_agent.ainvoke(
        {"messages": [HumanMessage(content=user_question)]}
    )

    return response["messages"][-1].content
