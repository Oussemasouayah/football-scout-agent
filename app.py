"""
🎨 Interface Streamlit — Football Scout Agent
Lance avec : streamlit run app.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
from agent.football_agent import create_football_agent

# ─────────────────────────────────────────────────────────────
# Configuration de la page
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Football Scout Agent",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="expanded",
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a472a, #2d7a4f);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #e8f5e9;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #2d7a4f;
    }
    .bot-message {
        background-color: #f5f5f5;
        padding: 12px;
        border-radius: 8px;
        margin: 8px 0;
        border-left: 4px solid #1565c0;
    }
    .example-btn {
        margin: 4px 0;
    }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Initialisation de l'état de session
# ─────────────────────────────────────────────────────────────

if "agent" not in st.session_state:
    with st.spinner("⚙️ Initialisation de l'agent..."):
        try:
            st.session_state.agent = create_football_agent()
            st.session_state.agent_ready = True
        except Exception as e:
            st.session_state.agent_ready = False
            st.session_state.agent_error = str(e)

if "messages" not in st.session_state:
    st.session_state.messages = []


# ─────────────────────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
    <h1>⚽ Football Scout Agent</h1>
    <p>Votre analyste IA football personnel — Powered by Groq LLaMA 3</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────

with st.sidebar:
     
    st.subheader("💡 Exemples de questions")
    
    examples = [
        "Quelles sont les stats de Mbappé ?",
        "Compare Haaland et Salah",
        "Top 5 meilleurs buteurs",
        "Filtre les attaquants avec plus de 20 buts",
        "Classement de la Premier League",
        "Matchs en direct maintenant",
        "Derniers matchs du Real Madrid",
    ]
    
    for example in examples:
        if st.button(f"💬 {example}", key=example, use_container_width=True):
            st.session_state.example_input = example
    
    st.divider()
    
    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        if "agent" in st.session_state:
            try:
                st.session_state.agent.memory.clear()
            except:
                pass
        st.rerun()


# ─────────────────────────────────────────────────────────────
# Zone de chat
# ─────────────────────────────────────────────────────────────

# Affichage de l'historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
        st.markdown(msg["content"])

# Input utilisateur
if not st.session_state.get("agent_ready", False):
    st.error(f"❌ Erreur d'initialisation : {st.session_state.get('agent_error', 'Inconnue')}")
    st.info("💡 Vérifiez que GROQ_API_KEY est définie dans votre fichier .env")
else:
    # Vérifier si un exemple a été cliqué
    prefill = st.session_state.pop("example_input", None)
    
    user_input = st.chat_input(
        "Posez votre question sur le football...",
        key="chat_input"
    )
    
    if prefill:
        user_input = prefill
    
    if user_input:
        # Afficher le message utilisateur
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_input)
        
        # Obtenir la réponse de l'agent
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("⚙️ L'agent réfléchit..."):
                try:
                    result = st.session_state.agent.invoke({"input": user_input})
                    response = result["output"]
                except Exception as e:
                    response = f"❌ Erreur : {str(e)}"
            
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# Message de bienvenue si pas encore de messages
if not st.session_state.messages and st.session_state.get("agent_ready", False):
    st.info("👋 Bonjour ! Je suis FootBot, votre scout IA. Posez-moi une question sur le football ou cliquez sur un exemple dans la sidebar !")
