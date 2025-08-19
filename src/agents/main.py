from typing import Annotated, Sequence, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.graph.message import add_messages, StateGraph
from src.prompts.main_agent_prompt import MAIN_AGENT_PROMPT, SUMMARIZER_PROMPT
from src.agents.stock_agent import stock_agent_run
from src.agents.currency_agent import currency_agent_run
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import START, END
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import Optional
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


# Estrutura a ser retornada pelo agente supervisor
# Cada ferramenta terá seu próprio input baseado no questionário do usuário
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


# Estado do grafo
# A propriedade supervisor_response só será retornada caso não haja sub agents para ser chamado
class MainAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    supervisor_response: Optional[SupervisorResponse]
    agents_results: Annotated[Sequence[BaseMessage], add_messages]


model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


async def stock_agent(state: MainAgentState):

    resp = state["supervisor_response"]
    if resp and resp.stock_agent_input:
        result = await stock_agent_run(resp.stock_agent_input)
        return {"agents_results": [result]}
    return {"agents_results": []}


async def currency_agent(state: MainAgentState):

    resp = state["supervisor_response"]
    if resp and resp.currency_agent_input:
        result = await currency_agent_run(resp.currency_agent_input)
        return {"agents_results": [result]}
    return {"agents_results": []}



  


async def aggregator(state: MainAgentState):

    resp = state["supervisor_response"]

    # Caso não haja agentes, retorna resposta do supervisor direto
    if not resp or not resp.agents_to_call:
        response_content = ""
        if resp is not None and getattr(resp, "response", None) is not None:
            response_content = resp.response
        return {"messages": [AIMessage(content=response_content or "")]}

    results = state.get("agents_results") or []
    msgs_str = "\n".join(str(m) for m in results)

    response = await model.ainvoke(SUMMARIZER_PROMPT.format(msgs=msgs_str))
    return {"messages": [AIMessage(content=response.content)]}


async def supervisor(state: MainAgentState):
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

    return {"supervisor_response": response}


workflow = StateGraph(MainAgentState)
checkpointer = InMemorySaver()
workflow.add_node("supervisor", supervisor)
workflow.add_node("stock_agent", stock_agent)
workflow.add_node("currency_agent", currency_agent)
workflow.add_node("aggregator", aggregator)


workflow.add_edge(START, "supervisor")

workflow.add_conditional_edges(
    "supervisor",
    lambda state: state["supervisor_response"].agents_to_call or ["aggregator"],
    {
        "stock_agent": "stock_agent",
        "currency_agent": "currency_agent",
        "aggregator": "aggregator",
    },
)

workflow.add_edge("stock_agent", "aggregator")
workflow.add_edge("currency_agent", "aggregator")
workflow.add_edge("aggregator", END)

supervisor_graph = workflow.compile(checkpointer=checkpointer)
