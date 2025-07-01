from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests # Importer la bibliothèque requests
import json     # Importer la bibliothèque json pour manipuler les données JSON
import os       # Importer la bibliothèque os pour accéder aux variables d'environnement

# --- Suppression des lignes liées à python-dotenv ---
# from dotenv import load_dotenv
# load_dotenv() # Cette ligne n'est plus nécessaire

app = FastAPI(
    title="Générateur de Landing Page API",
    description="API pour générer des pages d'atterrissage HTML en utilisant Google Gemini (via requêtes HTTP directes).",
    version="1.0.0"
)

# Récupérer la clé API Gemini directement depuis les variables d'environnement du système
# Sur Render, vous définirez GEMINI_API_KEY dans leurs paramètres de variables d'environnement.
API_KEY = os.getenv('GEMINI_API_KEY')
if not API_KEY:
    # Sur un environnement d'hébergement, cette erreur signifierait que la clé n'a pas été configurée.
    raise ValueError("La variable d'environnement GEMINI_API_KEY n'est pas définie. Veuillez la définir dans les variables d'environnement du service d'hébergement (par exemple, Render).")

# Point de terminaison de l'API Gemini (pour le modèle Gemini 2.0 Flash)
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
# Si vous utilisez un autre modèle comme 'gemini-pro', changez le nom du modèle dans l'URL.

class LandingPagePrompt(BaseModel):
    prompt: str

@app.post("/generate-landing-page", summary="Générer une page d'atterrissage HTML", response_description="Le contenu HTML généré")
async def generate_landing_page(lp_prompt: LandingPagePrompt):
    """
    Génère le code HTML complet pour une landing page responsive et moderne
    en utilisant Tailwind CSS basée sur la description textuelle fournie,
    en appelant l'API Gemini directement via HTTP.
    """
    if not lp_prompt.prompt:
        raise HTTPException(status_code=400, detail="Le prompt ne peut pas être vide.")

    # Construire le prompt pour Gemini
    gemini_instruction_prompt = f"""
    Générez le code HTML complet pour une landing page responsive et moderne en utilisant Tailwind CSS.
    Le contenu de la page doit être basé sur la description suivante :
    "{lp_prompt.prompt}"

    Assurez-vous que le HTML inclut :
    1.  Une balise `<!DOCTYPE html>` et les balises `<html>`, `<head>`, `<body>`.
    2.  Le CDN de Tailwind CSS dans le `<head>`: `<script src="https://cdn.tailwindcss.com"></script>`.
    3.  Une balise `<meta name="viewport" content="width=device-width, initial-scale=1.0">`.
    4.  Un titre approprié dans la balise `<title>`.
    5.  Des sections claires (Hero, Fonctionnalités, Témoignages, Appel à l'action, Contact, Pied de page).
    6.  Des classes Tailwind CSS pour un design esthétique et responsive.
    7.  Des placeholders pour les images si nécessaire (e.g., https://placehold.co/800x500/A855F7/FFFFFF?text=Image).
    8.  Le HTML doit être valide et bien structuré.

    Ne générez PAS de JavaScript pour des fonctionnalités dynamiques (comme l'envoi de formulaire), sauf si c'est pour des animations CSS ou des interactions simples qui ne nécessitent pas de backend.
    Le code généré doit être UNIQUEMENT le HTML.
    """

    # Préparer le corps de la requête JSON pour l'API Gemini
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": gemini_instruction_prompt}
                ]
            }
        ]
    }

    # Définir les en-têtes pour la requête HTTP
    headers = {
        'Content-Type': 'application/json'
    }

    try:
        # Envoyer la requête POST à l'API Gemini
        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status() # Lève une HTTPException pour les codes d'état 4xx/5xx

        # Analyser la réponse JSON
        result = response.json()

        # Extraire le contenu généré
        generated_html = ""
        if result.get("candidates") and len(result["candidates"]) > 0 and \
           result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts") and \
           len(result["candidates"][0]["content"]["parts"]) > 0:
            generated_html = result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            # Gérer les cas où la réponse est valide mais ne contient pas le HTML attendu
            raise HTTPException(status_code=500, detail="L'API Gemini n'a pas retourné de contenu HTML valide.")

        return {"html_content": generated_html}

    except requests.exceptions.RequestException as e:
        # Capturer les erreurs de connexion ou les erreurs HTTP de l'API Gemini
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'appel à l'API Gemini: {e}")
    except json.JSONDecodeError:
        # Capturer les erreurs si la réponse n'est pas un JSON valide
        raise HTTPException(status_code=500, detail="Erreur de décodage JSON de la réponse de l'API Gemini.")
    except Exception as e:
        # Capturer toute autre exception inattendue
        raise HTTPException(status_code=500, detail=f"Une erreur inattendue est survenue: {e}")
