import streamlit as st
import google.generativeai as genai

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="SAFE BET ENGINE V8", page_icon="🔮", layout="wide")

# Style Cyberpunk / Mode Sombre
st.markdown("""
    <style>
    .main { background-color: #060b14; color: #c8d8e8; }
    div.stButton > button {
        background-color: #001a2e; color: #00e5ff; 
        border: 1px solid #00e5ff44; border-radius: 10px;
        width: 100%;
        font-weight: bold;
    }
    div.stButton > button:hover { border-color: #00e5ff; box-shadow: 0 0 8px #00e5ff66; }
    .stChatMessage { border-radius: 12px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. CONFIGURATION DE L'IA (PROMPT SYSTEME)
SYSTEM_PROMPT = """Tu es SAFE BET ENGINE PRO V8.
SPECIALISATION : FOOTBALL UNIQUEMENT.

MISSION :
- Analyser les statistiques fournies par l'utilisateur (Historique, Live ou xG).
- Calculer rigoureusement un Score de Confiance Global sur 100.
- Estimer les probabilités via un modèle mathématique (Loi de Poisson ou simulation de puissance offensive).
- Calculer obligatoirement l'Edge sur la base des cotes fournies par l'utilisateur (Formule : Edge = (Probabilité * Cote) - 1).

STRUCTURE D'ANALYSE IMPOSÉE :
## 🏟️ 1. CONTEXTE ET ANALYSE DES DONNÉES
## 📊 2. SCORE DE CONFIANCE (Tableau Markdown)
## 📐 3. PROBABILITES ET CALCUL EDGE (Tableau Marché | Proba Modèle % | Cote Bookmaker | Edge %)
## 🏆 4. TOP RECOMMANDATIONS VALUE BET (Uniquement si Edge > 4% et Score > 70)

TONE : Ultra-professionnel, factuel, structuré en tableaux markdown, avec des emojis de section."""

# 3. BARRE LATÉRALE - PARAMÈTRES
st.sidebar.title("Configuration App ⚙️")
gemini_key = st.sidebar.text_input("Clé API Gemini (Google)", type="password", value="")

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Mode d'emploi")
st.sidebar.write("Colle directement les informations ou stats de ton match (depuis Flashscore ou Sofascore) dans le chat ci-dessous pour obtenir l'analyse complète d'Edge.")

# 4. INTERFACE PRINCIPALE
st.title("🔮 SAFE BET ENGINE V8")
st.caption("Moteur d'analyse prédictive indépendant.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. LOGIQUE DE CHAT AUTONOME
if user_query := st.chat_input("Ex: Analyse France vs Italie, cotes 1.90 / 3.40 / 4.10, xG récents 1.8 et 1.2..."):
    with st.chat_message("user"):
        st.markdown(user_query)
        
    with st.chat_message("assistant"):
        if not gemini_key:
            st.error("❌ Ajoute ta clé API Gemini dans la barre de gauche.")
        else:
            # CORRECTION ICI : st.spinner avec un 's' minuscule
            with st.spinner("Calculs en cours par le moteur V8..."):
                try:
                    genai.configure(api_key=gemini_key)
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=SYSTEM_PROMPT
                    )
                    
                    response = model.generate_content(user_query)
                    ai_response = response.text
                    
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "user", "content": user_query})
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                    
                except Exception as e:
                    st.error(f"❌ Erreur : {str(e)}")
