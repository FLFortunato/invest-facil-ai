import asyncio
from langchain_core.messages import HumanMessage, AIMessage
from src.agents.main import supervisor_graph


async def stream_graph_updates(user_input: str):
    """
    Recebe input do usuário e faz streaming em tempo real das respostas
    de todos os sub-agents do supervisor_graph.
    """
    # O astream retorna eventos parciais do LLM
    async for event in supervisor_graph.astream(
        {"messages": [HumanMessage(content=user_input)]}
    ):
        for node_name, value in event.items():
            messages = value.get("messages", [])
            if not messages:
                continue

            last_msg = messages[-1]

            if isinstance(last_msg, HumanMessage):
                print(f"[{node_name}] User: {last_msg.content}")
            elif isinstance(last_msg, AIMessage):
                # streaming de tokens
                content = last_msg.content or ""
                print(f"[{node_name}] Assistant: {content}", end="\r")  # parcial
            # else:
            #     # qualquer outra mensagem
            #     print(f"[{node_name}] {last_msg}", end="\r")
        await asyncio.sleep(0.01)  # evita travar o loop


async def main():
    """
    Loop de input do usuário com streaming
    """
    print("Digite 'quit' ou 'exit' para sair.")
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        try:
            await stream_graph_updates(user_input)
            print()  # pular linha após resposta completa
        except Exception as e:
            print("===================ERROR================", e)


# rodar apenas um loop de eventos
asyncio.run(main())
