import streamlit as st
import vertexai
from vertexai.preview import reasoning_engines

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="ORI - L'Étudiant", page_icon="🎓", layout="centered")

# --- CSS PERSONNALISÉ ---
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        height: 100px;
        border-radius: 20px;
        border: 2px solid #00B17A;
        background-color: white;
        color: #00B17A;
        font-size: 18px;
        font-weight: bold;
        transition: 0.3s;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button:hover {
        background-color: #00B17A;
        color: white;
        border-color: #00B17A;
        transform: scale(1.02);
    }
    .titre-ori {
        color: #00B17A;
        font-weight: 900;
        text-align: center;
        font-size: 3.5rem;
        margin-bottom: 0px;
    }
    .sous-titre {
        text-align: center;
        color: #666666;
        font-size: 1.1rem;
        margin-bottom: 40px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='titre-ori'>🎓 ORI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sous-titre'>Ton conseiller d'orientation intelligent par <b>L'Étudiant</b></p>", unsafe_allow_html=True)

# --- INITIALISATION DE LA VRAIE IA ---
@st.cache_resource
def charger_ia():
    PROJECT_ID = "letudiant-data-prod"
    reasoning_engine_id = "7428309353347678208"
    vertexai.init(project=PROJECT_ID, location="europe-west1")
    return reasoning_engines.ReasoningEngine(reasoning_engine_id)

try:
    ia = charger_ia()
    st.session_state.ia_disponible = True
except Exception as e:
    st.error("Le serveur IA est actuellement en maintenance.")
    st.session_state.ia_disponible = False

# --- INITIALISATION DES ÉTATS (MÉMOIRE) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "etape_profilage" not in st.session_state:
    st.session_state.etape_profilage = 0
if "profil" not in st.session_state:
    st.session_state.profil = {}

# --- AFFICHAGE CHAT CLASSIQUE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- LOGIQUE DE CONVERSATION ---
if prompt := st.chat_input("Ex: Je suis en Terminale et je ne sais pas quoi faire..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    mots_cles_doute = ["perdu", "sais pas", "aucune idée", "aide", "choisir"]
    
    with st.chat_message("assistant"):
        if any(mot in prompt.lower() for mot in mots_cles_doute):
            reponse = "Je vois que tu hésites, c'est tout à fait normal ! Laisse-moi t'aider à y voir plus clair en 2 petites questions. 🧭"
            st.markdown(reponse)
            st.session_state.messages.append({"role": "assistant", "content": reponse})
            st.session_state.etape_profilage = 1 
            st.rerun()
        else:
            st.session_state.etape_profilage = 0
            if st.session_state.ia_disponible:
                with st.spinner("ORI réfléchit..."):
                    try:
                        resultat = ia.query(config={"thread_id": "1"}, message=prompt)
                        st.markdown(str(resultat))
                        st.session_state.messages.append({"role": "assistant", "content": str(resultat)})
                    except Exception as e:
                        # Si on pose une question classique et que l'IA plante, on met un message propre
                        st.warning("⚠️ ORI est actuellement en maintenance pour le hackathon. Mais si tu me dis que tu es **perdu**, j'ai un parcours spécial pour toi ! 😉")

# ==========================================
# 🌳 ARBRE DE DÉCISION (VOTRE FLOW)
# ==========================================

# ÉTAPE 1 : Le domaine
if st.session_state.etape_profilage == 1:
    st.markdown("---")
    st.progress(33, text="Étape 1 sur 2 : Tes centres d'intérêt")
    st.write("### 🎯 Qu'est-ce qui t'attire le plus ?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💻\nLe Numérique / La Tech"):
            st.session_state.profil["domaine"] = "le numérique, la tech ou l'informatique"
            st.session_state.etape_profilage = 2
            st.rerun()
    with col2:
        if st.button("🤝\nL'Humain / Le Social"):
            st.session_state.profil["domaine"] = "l'humain, le social ou l'aide à la personne"
            st.session_state.etape_profilage = 2
            st.rerun()

# ÉTAPE 2 : La durée
elif st.session_state.etape_profilage == 2:
    st.markdown("---")
    st.progress(66, text="Étape 2 sur 2 : Ton rythme d'études")
    st.write("### 📚 Comment envisages-tu tes études ?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀\nÉtudes courtes\n(2 à 3 ans, BTS/BUT)"):
            st.session_state.profil["etudes"] = "courtes (2 à 3 ans maximum, type BTS ou BUT)"
            st.session_state.etape_profilage = 3
            st.rerun()
    with col2:
        if st.button("🎓\nÉtudes longues\n(5 ans, Master/Ingé)"):
            st.session_state.profil["etudes"] = "longues (niveau Bac+5, Master ou école d'ingénieur)"
            st.session_state.etape_profilage = 3
            st.rerun()

# ÉTAPE 3 : Requête à la vraie IA avec le RAG (et Fallback de sécurité)
elif st.session_state.etape_profilage == 3:
    st.markdown("---")
    st.progress(100, text="Analyse de ton profil terminée ! ✅")
    
    with st.chat_message("assistant"):
        st.success("C'est noté ! Je fouille dans la base de données de L'Étudiant pour te trouver les meilleures options...")
        
        if st.session_state.ia_disponible:
            with st.spinner("L'IA interroge le RAG..."):
                # On fabrique dynamiquement le prompt avec les choix de l'utilisateur !
                prompt_secret = f"""
                Agis comme un conseiller d'orientation expert. 
                L'utilisateur cherche une formation ou un métier dans ce domaine : {st.session_state.profil['domaine']}.
                Il souhaite faire des études : {st.session_state.profil['etudes']}.
                En te basant strictement sur tes données (RAG), trouve-lui 3 métiers ou formations qui correspondent parfaitement à ces critères. 
                Réponds avec une liste à puces claire et donne un petit conseil pour la suite.
                """
                
                try:
                    # 1. ON TENTE LA VRAIE IA
                    resultat = ia.query(config={"thread_id": "1"}, message=prompt_secret)
                    reponse_ia = str(resultat)
                    st.markdown(reponse_ia)
                    st.session_state.messages.append({"role": "assistant", "content": reponse_ia})
                    
                except Exception as e:
                    # 2. LE SERVEUR PLANTE ? ON ACTIVE LE PARACHUTE (Mock) !
                    st.warning("⚠️ L'IA de L'Étudiant est en maintenance, voici une réponse simulée pour la démo :")
                    
                    reponse_secours = f"""Voici 3 idées basées sur ton profil (**{st.session_state.profil['domaine']}** avec études **{st.session_state.profil['etudes']}**) :
* 🔹 **Développeur Web / Data Analyst** : Des métiers d'avenir très recherchés !
* 🔹 **Ingénieur ou Chef de projet** : Pour piloter des équipes.
* 🔹 **Responsable produit (Product Manager)** : Un mix entre technique et stratégie.

*Conseil : N'hésite pas à aller aux portes ouvertes pour en savoir plus !*"""
                    
                    st.markdown(reponse_secours)
                    st.session_state.messages.append({"role": "assistant", "content": reponse_secours})
                
                # Call to action business (Salons de l'Étudiant) toujours affiché, que l'IA ait marché ou non
                st.info("📍 **Passe à l'action !** Découvre ces formations en vrai au prochain **Salon de l'Étudiant**. [Trouver le salon le plus proche →](https://www.letudiant.fr/etudes/salons.html)")
                
        else:
            st.error("L'IA n'est pas connectée pour le moment.")
        
        # On remet à zéro pour permettre un nouveau test
        st.session_state.etape_profilage = 0