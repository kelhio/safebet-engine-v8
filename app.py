import streamlit as st
import requests
import json

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="SAFE BET ENGINE V8", page_icon="🔮", layout="wide")

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
- Identifier uniquement les paris à forte probabilité basés sur des données vérifiables.
- Ne jamais inventer de statistiques, blessures ou informations.
- Maximiser la fiabilité. Minimiser le nombre de paris proposés.
- Refuser les matchs insuffisamment documentés.

═══════════════════════════════════════
SCORE DE CONFIANCE GLOBAL
═══════════════════════════════════════
Calculer pour chaque match un Score Global sur 100 :
- Forme récente : 30%
- xG / xGA : 25%
- Absences importantes : 15%
- Motivation : 10%
- Historique H2H : 10%
- Domicile/Extérieur : 10%

Interprétation :
- 90-100 → ELITE ⭐⭐⭐⭐⭐
- 80-89  → FORTE CONFIANCE ⭐⭐⭐⭐
- 70-79  → MODERE ⭐⭐⭐
- < 70   → AUCUN PARI — match rejeté

═══════════════════════════════════════
FILTRE ANTI-PIEGE
═══════════════════════════════════════
REJETER le match si moins de 5 matchs récents dispo, + de 3 absents, rotation massive, météo extrême.

═══════════════════════════════════════
STRUCTURE D'UNE ANALYSE COMPLETE IMPOSÉE
═══════════════════════════════════════
## 🏟️ 1. CONTEXTE ET ACTUALITE TEMPS REEL (Incorpore les stats fournies par l'API)
## 📊 2. SCORE DE CONFIANCE (Tableau Markdown)
## 📐 3. PROBABILITES ET CALCUL EDGE (Tableau Marché | Proba Modèle % | Cote | Edge %)
## 🏆 4. TOP RECOMMANDATIONS VALUE BET (Uniquement si Edge > 4% et Score > 70)

TONE : Ultra-professionnel, factuel, tableaux markdown, emojis de section. Jamais de pronostic direct."""

# 3. BARRE LATÉRALE — CONFIGURATION DES CLÉS API
st.sidebar.title("Configuration App ⚙️")
anthropic_key = st.sidebar.text_input("Clé API Anthropic (Claude)", type="password", value="")
rapidapi_key = st.sidebar.text_input("Clé RapidAPI (Football)", type="password", value="f57504f6a9mshcf02caa7b64be87p11b83ajsnd9bf6340fa9d")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎫 Récupération Manuelle des Stats")
event_id_input = st.sidebar.text_input("Entrer un Match ID (Event ID)", value="4621624")

# 4. FONCTIONS DE RÉCUPÉRATION DES DONNÉES
def fetch_football_stats(event_id):
    """Interroge l'API Football sur RapidAPI pour avoir les statistiques brutes du match"""
    if not rapidapi_key:
        return "⚠️ Clé RapidAPI manquante dans la barre latérale."
    
    url = "https://free-api-live-football-data.p.rapidapi.com/football-get-match-event-all-stats"
    querystring = {"eventid": event_id}
    headers = {
        "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com",
        "x-rapidapi-key": rapidapi_key
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            return response.json()
        return f"Erreur API (Code {response.status_code})"
    except Exception as e:
        return f"Impossible de joindre l'API de statistiques : {str(e)}"

def call_claude(history, user_message, context_data=None):
    """Envoie l'historique, le prompt système et le contexte de l'API à Claude"""
    if not anthropic_key:
        st.error("❌ Tu dois renseigner ta clé API Anthropic dans la barre latérale pour activer Claude.")
        return None
        
    headers = {
        "x-api-key": anthropic_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    
    # Intégration des données API directement dans la requête actuelle
    full_content = user_message
    if context_data:
        full_content += f"\n\n[DONNÉES TEMPS RÉEL FOURNIES PAR L'API FOOTBALL EN JSON] :\n{json.dumps(context_data, ensure_ascii=False)[:6000]}"
    
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": full_content})
    
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 4000,
        "system": SYSTEM_PROMPT,
        "messages": messages
    }
    
    try:
        res = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
        return res.json()['content'][0]['text']
    except Exception as e:
        st.error(f"Erreur technique Claude : {e}")
        return None

# 5. INITIALISATION DE L'INTERFACE PRINCIPALE
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🔮 SAFE BET ENGINE V8")
st.caption("Application connectée aux flux de données football temps réel via API")

# Affichage de l'historique du chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Bouton d'action rapide pour analyser l'ID de la barre latérale
if st.sidebar.button("📊 Analyser ce Match ID"):
    with st.spinner("Extraction des statistiques brutes du match..."):
        api_data = fetch_football_stats(event_id_input)
        
    with st.chat_message("user"):
        user_text = f"Analyse complète du match avec l'ID d'évènement : {event_id_input}"
        st.markdown(user_text)
        
    with st.chat_message("assistant"):
        with st.spinner("Le modèle Safe Bet étudie le flux de données..."):
            ai_response = call_claude(st.session_state.messages, user_text, context_data=api_data)
            if ai_response:
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "user", "content": user_text})
                st.session_state.messages.append({"role": "assistant", "content": ai_response})

# Zone de Chat standard libre
if user_query := st.chat_input("Pose une question ou demande une commande (/safe, ACCUEIL...)"):
    with st.chat_message("user"):
        st.markdown(user_query)
        
    with st.chat_message("assistant"):
        with st.spinner("Analyse du moteur en cours..."):
            ai_response = call_claude(st.session_state.messages, user_query)
            if ai_response:
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "user", "content": user_query})
                st.session_state.messages.append({"role": "assistant", "content": ai_response})