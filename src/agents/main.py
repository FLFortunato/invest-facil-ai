from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages, StateGraph
from src.prompts.main_agent_prompt import MAIN_AGENT_PROMPT, SUMMARIZER_PROMPT
from src.agents.stock_agent import stock_agent_run
from src.agents.currency_agent import currency_agent_run
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, END
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional
import asyncio
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()


class SupervisorResponse(BaseModel):
    agents_to_call: list = Field(
        description="""
        List containing the name of the agents to be invoked. These agents are the followings:
        stock_agent: This agent deals with everything related to stock market like data about a company and stock price.
        currency_agent: This agent deals with everything related to currencies like updated prices a history.
        """
    )
    stock_agent_input: Optional[str] = Field(
        description="The extracted part of the user input that is related to stock_agent"
    )
    currency_agent_input: Optional[str] = Field(
        description="The extracted part of the user input that is related to currency_agent"
    )
    response: Optional[str] = Field(
        description="If no agent is to be called, return a friendly response in reply to the user input."
    )


class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


model = ChatOpenAI(model="gpt-4.1")


async def run_sub_agents(response: SupervisorResponse):

    if response and response.agents_to_call and len(response.agents_to_call) <= 0:
        return

    agent_mapping = {
        "stock_agent": stock_agent_run,
        "currency_agent": currency_agent_run,
    }

    agents_to_call = response.agents_to_call

    tasks = []

    for sub_agent in agents_to_call:
        agent = agent_mapping[sub_agent]
        agent_input = getattr(response, f"{sub_agent}_input")
        executable = asyncio.create_task(agent(agent_input))  # type: ignore
        tasks.append(executable)

    if len(tasks) > 0:
        results = await asyncio.gather(*tasks)

        return results


async def aggregator(msgs) -> str | None:

    if msgs and len(msgs) > 0:
        # Ensure msgs is a string for the prompt
        if isinstance(msgs, list):
            # Convert list elements to string and join them
            msgs_str = "\n".join(str(m) for m in msgs)
        else:
            msgs_str = str(msgs)

        response = await model.ainvoke(SUMMARIZER_PROMPT.format(msgs=msgs_str))

        return str(response.content)


async def supervisor(state: State) -> State:
    parser = PydanticOutputParser(pydantic_object=SupervisorResponse)

    prompt = ChatPromptTemplate.from_template(MAIN_AGENT_PROMPT)

    chain = prompt | model | parser

    all_messages = state["messages"]
    conversation_history = "\n".join(
        str(msg.content)
        for msg in all_messages
        if hasattr(msg, "content") and isinstance(msg.content, str)
    )

    response = await chain.ainvoke(
        {
            "user_input": state["messages"][-1].content or "",
            "format_instructions": parser.get_format_instructions(),
            "conversation_history": conversation_history,
        }
    )

    agents_response = await run_sub_agents(response)

    results = await aggregator(agents_response)

    final_result = ""

    if not agents_response:
        final_result = response.response or ""
    else:
        final_result = results

    return {
        "messages": [AIMessage(content=final_result or "")],
    }


workflow = StateGraph(State)
checkpointer = InMemorySaver()
workflow.add_node("supervisor", supervisor)
workflow.add_edge(START, "supervisor")
workflow.add_edge("supervisor", END)

supervisor_graph = workflow.compile(checkpointer=checkpointer)
