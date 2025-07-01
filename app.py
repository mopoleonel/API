# app.py - Adapté pour fonctionner avec l'API en ligne sur Render

import streamlit as st
import requests
import json
import os # os est toujours nécessaire pour d'autres usages Streamlit, mais pas pour dotenv ici

# --- Suppression des lignes liées à python-dotenv ---
# from dotenv import load_dotenv
# load_dotenv() # Cette ligne n'est plus nécessaire

# --- Configuration de l'application Streamlit ---
st.set_page_config(page_title="Générateur de Landing Page IA", layout="wide")
st.title("🚀 Générateur de Landing Page avec IA")
st.markdown("Décrivez la landing page que vous souhaitez, et notre IA la générera pour vous !")

# --- Configuration du point de terminaison de l'API FastAPI en ligne ---
# URL de votre API FastAPI déployée sur Render
# Remplacez 'https://mon-api-landing-page.onrender.com' par l'URL réelle de votre service Render
FASTAPI_URL = "https://mon-api-landing-page.onrender.com"
GENERATE_ENDPOINT = f"{FASTAPI_URL}/generate-landing-page"

# --- Interface Streamlit ---
col1, col2 = st.columns([1, 2])

with col1:
    st.header("Décrivez votre page")
    user_prompt = st.text_area(
        "Décrivez votre landing page ici (ex: 'Une landing page moderne et minimaliste pour un service de coaching en ligne, avec un bouton d'appel à l'action pour s'inscrire à une session gratuite, et des témoignages.')",
        height=250,
        placeholder="Décrivez le contenu, le style, les sections, et les appels à l'action de votre landing page..."
    )

    if st.button("Générer la Landing Page", type="primary"):
        if user_prompt:
            loading_message_placeholder = st.empty()
            loading_message_placeholder.info("Génération en cours... Veuillez patienter quelques instants. Cela peut prendre un certain temps.")

            try:
                payload = {"prompt": user_prompt}
                headers = {"Content-Type": "application/json"}

                # Envoi de la requête à l'API FastAPI en ligne
                response = requests.post(GENERATE_ENDPOINT, headers=headers, data=json.dumps(payload))
                response.raise_for_status() # Lève une HTTPException pour les codes d'état 4xx/5xx

                result = response.json()
                generated_html = result.get("html_content", "")

                if not generated_html:
                    loading_message_placeholder.warning("L'API a répondu mais aucun contenu HTML n'a été trouvé.")
                    st.session_state.generated_html = ""
                else:
                    st.session_state.generated_html = generated_html
                    st.session_state.show_preview = True
            except requests.exceptions.RequestException as e:
                loading_message_placeholder.error(f"Erreur lors de la connexion à l'API en ligne: {e}")
                st.error(f"Veuillez vérifier que l'API FastAPI est bien accessible à l'adresse {FASTAPI_URL}.")
                st.session_state.generated_html = ""
                st.session_state.show_preview = False
            except json.JSONDecodeError:
                loading_message_placeholder.error("Erreur : La réponse de l'API n'est pas un JSON valide.")
                st.session_state.generated_html = ""
                st.session_state.show_preview = False
            except Exception as e:
                loading_message_placeholder.error(f"Une erreur inattendue est survenue: {e}")
                st.session_state.generated_html = ""
                st.session_state.show_preview = False
            finally:
                loading_message_placeholder.empty() # Efface le message de chargement
        else:
            st.warning("Veuillez saisir une description pour générer la landing page.")
            st.session_state.generated_html = ""
            st.session_state.show_preview = False
    else:
        # Réinitialiser au chargement de la page ou si le bouton n'est pas pressé
        if "show_preview" not in st.session_state:
            st.session_state.show_preview = False
        if "generated_html" not in st.session_state:
            st.session_state.generated_html = ""


# --- Section d'aperçu ---
with col2:
    st.header("Aperçu de la Landing Page")
    if st.session_state.show_preview and st.session_state.generated_html:
        st.success("Aperçu de la Landing Page générée :")
        # Utiliser components.v1.html pour rendre le HTML généré
        st.components.v1.html(st.session_state.generated_html, height=800, scrolling=True)
    else:
        st.info("Votre aperçu apparaîtra ici après la génération.")
