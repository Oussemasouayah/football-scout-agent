"""
Football Scout Agent — Tool Calling Agent (function calling natif Groq)
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools.player_tools import search_player, filter_players, compare_players, top_players
from tools.api_tools import get_live_matches, get_league_standings, get_recent_matches

load_dotenv()

TOOLS = [
    search_player,
    filter_players,
    compare_players,
    top_players,
    get_live_matches,
    get_league_standings,
    get_recent_matches,
]


def create_football_agent():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("❌ GROQ_API_KEY manquante dans le fichier .env")

    llm = ChatGroq(
        groq_api_key=api_key,
        model_name="llama-3.3-70b-versatile",
        temperature=0.1,
        max_tokens=1024,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """Tu es FootBot, un agent IA expert en football. Tu réponds toujours en français.

RÈGLES STRICTES pour utiliser les outils :
- search_player : passe UNIQUEMENT le nom, ex: Mbappe (jamais name="Mbappe")
- filter_players : passe position comme string simple ex: Attaquant, min_goals comme entier ex: 20
- compare_players : passe player1 et player2 comme strings simples ex: Haaland, Salah
- top_players : passe category comme string ex: buts, et limit comme entier ex: 5
- get_league_standings : passe league_id comme entier (39=PL, 140=LaLiga, 61=Ligue1) et season=2024
- get_live_matches : aucun paramètre
- get_recent_matches : passe team_name et last_n comme entier

RÈGLE CRITIQUE : pour CHAQUE question, appelle UN SEUL outil pertinent, lis son résultat,
puis réponds directement. N'enchaîne JAMAIS un deuxième outil différent sauf si la question
le demande explicitement. N'appelle JAMAIS le même outil deux fois avec les mêmes paramètres."""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm=llm, tools=TOOLS, prompt=prompt)

    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=True,
    )

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3,
        return_intermediate_steps=False,
    )


def run_cli():
    print("\n⚽ FOOTBALL SCOUT AGENT\nTapez 'exit' pour quitter.\n")
    try:
        agent = create_football_agent()
    except ValueError as e:
        print(e)
        return
    while True:
        try:
            user_input = input("Vous : ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                break
            result = agent.invoke({"input": user_input})
            print(f"\nFootBot : {result['output']}\n")
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    run_cli()