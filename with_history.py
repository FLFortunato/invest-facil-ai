from dotenv import load_dotenv

from typing import Annotated, List, Union
import asyncio

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

load_dotenv()


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[List[Union[HumanMessage, AIMessage]], add_messages]


graph_builder = StateGraph(State)

llm = ChatOpenAI(model="gpt-5-nano")


async def chatbot(state: State):
    messages = await llm.ainvoke(state["messages"])
    return {"messages": [messages]}


# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()


conversation_history = []


async def stream_graph_updates_async(user_input: str):
    global conversation_history
    conversation_history.append(HumanMessage(content=user_input))
    response = await graph.ainvoke({"messages": conversation_history})
    conversation_history = response["messages"]
    print("AI:", conversation_history[-1].content)


async def main():
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            await stream_graph_updates_async(user_input)
        except Exception as e:
            print("Error:", e)
            break


asyncio.run(main())
