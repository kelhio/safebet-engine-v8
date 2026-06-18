import streamlit as st
import requests
import json
from datetime import datetime

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="SAFE BET ENGINE V8 (Prediction API)", page_icon="🔮", layout="wide")

# Look & Feel Cyberpunk / Mode Sombre
st.markdown("""
    <style>
    .main { background-color: #060b14; color: #c8d8e8; }
    div.stButton > button {
        background-color: #001a2e; color: #00e5ff; 
        border: 1px solid #00e5ff44; border-radius: 10px;
        width: 100%;
    }
    div.stButton > button:hover { border-color: #00e5ff; box-shadow: 0 0 8px #00e5ff66; }
    .stChatMessage { border-radius: 12px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# 2. PROMPT SYSTEME DE REFERENCE
SYSTEM_PROMPT = """Tu es SAFE BET ENGINE PRO V8.
SPECIALISATION : FOOTBALL UNIQUEMENT.

MISSION :
- Analyser la liste des prédictions et probabilités fournies par l'API pour la date sélectionnée.
- Identifier les opportunités à forte probabilité en calculant l'Edge par rapport aux cotes du marché fournies.
- Présenter une analyse ultra-fiable et rejeter les opportunités trop risquées.

═══════════════════════════════════════
STRUCTURE D'UNE ANALYSE COMPLETE IMPOSÉE
═══════════════════════════════════════
## 🏟️ 1. SÉLECTION ET CONTEXTE DU MATCH
## 📊 2. SCORE DE CONFIANCE (Tableau Markdown)
## 📐 3. PROBABILITES ET CALCUL EDGE (Tableau Marché | Proba Modèle % | Cote | Edge %)
## 🏆 4. TOP RECOMMANDATIONS VALUE BET (Uniquement si Edge > 4% et Score > 70)

TONE : Ultra-professionnel, factuel, tableaux markdown, emojis de section."""

# 3. BARRE LATÉRALE — CONFIGURATION DES CLÉS
st.sidebar.title("Configuration App ⚙️")
gemini_key = st.sidebar.text_input("Clé API Gemini (Google)", type="password", value="")
rapidapi_key = st.sidebar.text_input("Clé RapidAPI", type="password", value="f57504f6a9mshcf02caa7b64be87p11b83ajsnd9bf6340fa9d")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎫 Paramètres de Recherche")

date_selectionnee = st.sidebar.date_input("Choisir une date à analyser", datetime.now())
iso_date_str = date_selectionnee.strftime("%Y-%m-%d")

# 4. FONCTION POUR RÉCUPÉRER LES PRÉDICTIONS PAR DATE
def fetch_predictions_by_date(date_str):
    """Interroge Football Prediction API"""
    if not rapidapi_key:
        return {"error": "⚠️ Clé RapidAPI manquante."}
    
    url = "https://football-prediction-api.p.rapidapi.com/api/v2/predictions"
    querystring = {"market": "classic", "iso_date": date_str}
    headers = {
        "x-rapidapi-host": "football-prediction-api.p.rapidapi.com",
        "x-rapidapi-key": rapidapi_key
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=20)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Erreur API (Code {response.status_code}). Vérifie ton abonnement sur RapidAPI."}
    except Exception as e:
        return {"error": f"Impossible de joindre l'API : {str(e)}"}

def call_gemini(user_message, context_data=None):
    """Envoie les données brutes à l'API Gemini avec l'identifiant exact requis"""
    if not gemini_key:
        st.error("❌ Tu dois renseigner ta clé API Gemini dans la barre latérale.")
        return None
        
    # CORRECTION ICI : Ajout du suffixe '-latest' exigé par l'API v1beta
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={gemini_key}"
    
    full_prompt = f"{SYSTEM_PROMPT}\n\n"
    if context_data:
        full_prompt += f"[DONNÉES ENTRANTES FOOTBALL PREDICTION API] :\n{json.dumps(context_data, ensure_ascii=False)[:7000]}\n\n"
    full_prompt += f"Demande utilisateur : {user_message}"
    
    payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=45)
        response_json = res.json()
        
        if 'candidates' in response_json:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in response_json:
            return f"❌ Erreur de l'API Gemini : {response_json['error'].get('message', 'Erreur inconnue')}"
        else:
            return f"❌ Réponse inattendue de l'API."
    except Exception as e:
        st.error(f"Erreur technique de connexion : {e}")
        return None

# 5. INTERFACE PRINCIPALE
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🔮 SAFE BET ENGINE V8 (Mode Prediction API)")
st.caption(f"Moteur connecté aux modèles mathématiques prédictifs.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.sidebar.button("📊 Analyser cette Date"):
    with st.spinner(f"Extraction des prédictions pour le {iso_date_str}..."):
        api_data = fetch_predictions_by_date(iso_date_str)
        
    with st.chat_message("user"):
        user_text = f"Analyse la liste des prédictions pour la date du : {iso_date_str}"
        st.markdown(user_text)
        
    with st.chat_message("assistant"):
        if "error" in api_data:
            st.error(api_data["error"])
        else:
            with st.spinner("Le robot cherche et calcule l'Edge sur les meilleurs matchs disponibles..."):
                prompt_enrichi = f"{user_text}. Pour le match sélectionné, applique des cotes du marché réalistes (ex: Home 2.10, Nul 3.30, Away 3.20) si elles ne sont pas incluses, puis calcule l'Edge."
                ai_response = call_gemini(prompt_enrichi, context_data=api_data)
                if ai_response:
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "user", "content": user_text})
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})

if user_query := st.chat_input("Pose une question ou donne un nom de match précis..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    with st.chat_message("assistant"):
        with st.spinner("Analyse Gemini..."):
            ai_response = call_gemini(user_query)
            if ai_response:
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "user", "content": user_query})
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
