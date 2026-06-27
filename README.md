# Football Scout Agent

Agent IA d'analyse football basé sur LangChain + Groq LLaMA 3.

## Installation

Créer un environnement virtuel et installer les dépendances :

    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

## Configuration

Créer un fichier .env à la racine avec vos clés API :

  GROQ_API_KEY=votre_cle_groq
  API_FOOTBALL_KEY=votre_cle_api_football

## Lancement

    streamlit run app.py

## Équipe

- Oussema Souayah — Agent LangChain & Orchestration
- Membre 2 — Tools externes (API Football)  
- Membre 3 — Tools internes (Base de données)
- Membre 4 — Interface Streamlit
- Membre 5 — Tests & Documentation