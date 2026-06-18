import streamlit as st
import requests
import json

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(page_title="SAFE BET ENGINE V8 (API-Football)", page_icon="🔮", layout="wide")

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
- Identifier uniquement les paris à forte probabilité basés sur des données historiques et statistiques détaillées.
- Calculer le score de confiance et estimer les probabilités à l'aide des données fournies (classement, forme, H2H).
- Maximiser la fiabilité.

═══════════════════════════════════════
STRUCTURE D'UNE ANALYSE COMPLETE IMPOSÉE
═══════════════════════════════════════
## 🏟️ 1. CONTEXTE ET ACTUALITE DES ÉQUIPES
## 📊 2. SCORE DE CONFIANCE (Tableau Markdown calculé sur la Forme, le Classement et le H2H)
## 📐 3. PROBABILITES ET CALCUL EDGE (Tableau Marché | Proba Modèle % | Cote | Edge %)
## 🏆 4. TOP RECOMMANDATIONS VALUE BET (Uniquement si Edge > 4% et Score > 70)

TONE : Ultra-professionnel, factuel, tableaux markdown, emojis de section."""

# 3. BARRE LATÉRALE — CONFIGURATION DES CLÉS
st.sidebar.title("Configuration App ⚙️")
gemini_key = st.sidebar.text_input("Clé API Gemini (Google)", type="password", value="")
rapidapi_key = st.sidebar.text_input("Clé RapidAPI", type="password", value="f57504f6a9mshcf02caa7b64be87p11b83ajsnd9bf6340fa9d")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎫 Paramètres du Match API-Football")
st.sidebar.info("Utilise un ID de match provenant d'API-Football (Exemple par défaut : 867946)")
fixture_id_input = st.sidebar.text_input("Entrer le Fixture ID (Match ID)", value="867946")

# 4. FONCTION POUR RÉCUPÉRER LES DONNÉES COMPLÈTES (LIVESTATS, H2H, FORME)
def fetch_complete_football_data(fixture_id):
    """Récupère le package complet du match sur la nouvelle API-Football"""
    if not rapidapi_key:
        return {"error": "⚠️ Clé RapidAPI manquante."}
    
    headers = {
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
        "x-rapidapi-key": rapidapi_key
    }
    
    base_url = "https://api-football-v1.p.rapidapi.com/v3"
    
    try:
        # 1. Infos du match et stats des équipes
        fix_res = requests.get(f"{base_url}/fixtures", headers=headers, params={"id": fixture_id}, timeout=15)
        if fix_res.status_code != 200 or not fix_res.json().get("response"):
            return {"error": f"Impossible de trouver le match ID {fixture_id} sur cette API."}
        
        fixture_data = fix_res.json()["response"][0]
        home_id = fixture_data["teams"]["home"]["id"]
        away_id = fixture_data["teams"]["away"]["id"]
        league_id = fixture_data["league"]["id"]
        season = fixture_data["league"]["season"]
        
        # 2. Récupération des face-à-face (H2H)
        h2h_res = requests.get(f"{base_url}/fixtures/headtohead", headers=headers, params={"h2h": f"{home_id}-{away_id}", "next": 5}, timeout=15)
        h2h_data = h2h_res.json().get("response", [])
        
        # 3. Classement de la ligue pour le contexte
        stand_res = requests.get(f"{base_url}/standings", headers=headers, params={"league": league_id, "season": season}, timeout=15)
        stand_data = stand_res.json().get("response", [])
        
        # Compilation du package de données pour Gemini
        complete_package = {
            "match_details": fixture_data,
            "head_to_head": h2h_data,
            "league_standings": stand_data
        }
        return complete_package
        
    except Exception as e:
        return {"error": f"Erreur de connexion API-Football : {str(e)}"}

def call_gemini(user_message, context_data=None):
    """Envoie les données et l'invite à l'API Gemini"""
    if not gemini_key:
        st.error("❌ Tu dois renseigner ta clé API Gemini dans la barre latérale.")
        return None
        
    # URL officielle v1 standardisée pour Gemini 1.5 Flash
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={gemini_key}"
    
    full_prompt = f"{SYSTEM_PROMPT}\n\n"
    if context_data:
        full_prompt += f"[DONNÉES ENTRANTES API-FOOTBALL (CONTEXTE COMPLET)] :\n{json.dumps(context_data, ensure_ascii=False)[:7000]}\n\n"
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
            return f"❌ Réponse inattendue : {response_json}"
    except Exception as e:
        st.error(f"Erreur technique de connexion : {e}")
        return None

# 5. INTERFACE PRINCIPALE
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🔮 SAFE BET ENGINE V8 (Mode API-SPORTS)")
st.caption("Moteur de pronostics football v8 connecté aux flux globaux historiques et temps réel.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.sidebar.button("📊 Analyser ce Match ID"):
    with st.spinner("Extraction de l'historique complet, H2H et classements..."):
        api_data = fetch_complete_football_data(fixture_id_input)
        
    with st.chat_message("user"):
        user_text = f"Analyse complète et calcul d'Edge pour le match ID : {fixture_id_input}"
        st.markdown(user_text)
        
    with st.chat_message("assistant"):
        if "error" in api_data:
            st.error(api_data["error"])
        else:
            with st.spinner("Le moteur Safe Bet étudie le package de données complet..."):
                # Injection automatique des cotes fictives/génériques si non fournies pour forcer l'analyse
                prompt_enrichi = f"{user_text}. Voici les cotes du marché : Victoire Domicile: 2.10, Nul: 3.20, Victoire Extérieure: 3.40. Calcule l'Edge obligatoire."
                ai_response = call_gemini(prompt_enrichi, context_data=api_data)
                if ai_response:
                    st.markdown(ai_response)
                    st.session_state.messages.append({"role": "user", "content": user_text})
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})

if user_query := st.chat_input("Pose une question ou injecte de nouvelles cotes..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    with st.chat_message("assistant"):
        with st.spinner("Analyse Gemini..."):
            ai_response = call_gemini(user_query)
            if ai_response:
                st.markdown(ai_response)
                st.session_state.messages.append({"role": "user", "content": user_query})
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
