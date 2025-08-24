from dotenv import load_dotenv
from pydantic import BaseModel
from langgraph.prebuilt import create_react_agent
from src.prompts.general_subject_agent_prompt import GENERAL_SUBJECT_PROMPT
from src.prompts.stock_agent_prompt import STOCK_AGENT_PROMPT
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.tools.tools import search_internet

load_dotenv()


chat_model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
)


general_subject_agent = create_react_agent(
    model=chat_model,
    tools=[search_internet],
    prompt=GENERAL_SUBJECT_PROMPT,
    name="general_subject_agent",
)


async def general_subject_agent_run(user_question: str):
    print("===================GENERAL SUBJECT AGENT====================", user_question)
    response = await general_subject_agent.ainvoke(
        {"messages": [HumanMessage(content=user_question)]}
    )

    return response["messages"][-1].content
