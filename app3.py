from flask import Flask, render_template, send_file, request, jsonify
import json
import os
from flask_cors import CORS  # Ajout pour activer CORS
from apikey import apikey
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Initialisation de l'application Flask
app = Flask(__name__, static_folder='static')
CORS(app)  # Activation de CORS pour permettre les requêtes cross-origin

# Dossier où stocker les scénarios validés
SCENARIOS_DIR = "scenarios"
os.makedirs(SCENARIOS_DIR, exist_ok=True)

# Clé API Groq
groq_api_key = apikey

# Initialisation du modèle Groq
llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=groq_api_key)

# Définition des prompts
prompt_generation = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant chargé de créer des scénarios immersifs précis et concis. "
               "Fournis les éléments suivants dans un format structuré :\n"
               "1. Une description concise de la situation d'urgence.\n"
               "2. Une liste numérotée des consignes à suivre.\n"
               "3. Une liste des étapes de validation correspondant aux consignes sous format nominal, sans doublons et ordonnées.\n"
               "Réponds uniquement avec ces éléments, sans commentaires supplémentaires."),
    ("user", "{requete}")
])

prompt_niveaux = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant chargé de créer des scénarios immersifs pour trois niveaux distincts :\n"
               "- Niveau Débutant : Formation guidée avec aides visuelles et auditives.\n"
               "- Niveau Intermédiaire : Réduction des aides avec des distractions.\n"
               "- Niveau Avancé : Limitation de temps et tâches simultanées.\n"
               "Pour chaque scénario, fournis les éléments suivants dans un format structuré :\n"
               "1. Une description de la situation d'urgence.\n"
               "2. Une liste numérotée des consignes à suivre.\n"
               "3. Une liste des étapes de validation correspondant aux consignes.\n"
               "Réponds uniquement avec ces éléments, sans commentaires supplémentaires."),
    ("user", "{requete}\nCrée un scénario adapté pour le niveau suivant : {niveau}.")
])

# Fonction pour générer un scénario structuré
def generer_scenario_structure(requete):
    try:
        query = prompt_generation.format(requete=requete)
        response = llm.invoke(query)
        reponse_texte = response.content.strip()
        
        sections = reponse_texte.split("\n\n")
        if len(sections) < 3:
            raise ValueError("Format de réponse inattendu.")
        
        description = sections[0].split("1. ")[-1].strip()
        consignes = [line.split(". ", 1)[-1].strip() for line in sections[1].split("\n") if line.strip()]
        etapes_validation = sorted(set(line.strip("- ") for line in sections[2].split("\n") if line.strip()))[1:]
        
        scenario = {
            "description": description,
            "consignes": consignes,
            "etapes_validation": {etape: False for etape in etapes_validation}
        }
        return scenario
    except Exception as e:
        print(f"Erreur lors de la génération du scénario : {e}")
        return None

# Route pour générer un scénario via API (compatible avec Unity)
@app.route('/generer', methods=['POST'])
def generer_scenario():
    data = request.get_json()  # Récupère les données JSON envoyées par Unity
    if not data or "requete" not in data:
        return jsonify({"error": "Données invalides"}), 400
    
    scenario = generer_scenario_structure(data["requete"])
    return jsonify(scenario), 200 if scenario else (jsonify({"error": "Échec de la génération du scénario"}), 500)

# Route pour générer des scénarios par niveaux (via formulaire HTML)
@app.route('/generer_niveaux', methods=['POST'])
def generer_scenarios_niveaux():
    requete = request.form.get("requete", "")
    niveaux = ["Débutant", "Intermédiaire", "Avancé"]
    scenarios = {}
    
    for niveau in niveaux:
        scenario = generer_scenario_structure(requete)
        if scenario:
            scenarios[niveau] = scenario
        else:
            scenarios[niveau] = {"error": f"Erreur lors de la génération du scénario pour le niveau {niveau}."}
    
    return render_template('index.html', scenarios_niveaux=scenarios, requete=requete)

# Route pour valider une étape
@app.route('/valider', methods=['POST'])
def valider_etape():
    try:
        scenario_json = request.form.get("scenario", "{}")
        etape_validee = request.form.get("etape", "").strip()

        scenario_dict = json.loads(scenario_json)

        if "etapes_validation" in scenario_dict and isinstance(scenario_dict["etapes_validation"], dict):
            if etape_validee in scenario_dict["etapes_validation"]:
                scenario_dict["etapes_validation"][etape_validee] = True
                validation_result = f"Étape '{etape_validee}' validée avec succès !"
            else:
                validation_result = "Étape non trouvée dans le scénario."
        else:
            validation_result = "Aucune étape de validation définie dans le scénario."

        return render_template('index.html', scenario=scenario_dict, validation_result=validation_result, show_validation=True)
    
    except json.JSONDecodeError:
        return render_template('index.html', error="Erreur: Le scénario fourni n'est pas un JSON valide.")
    except Exception as e:
        return render_template('index.html', error=f"Erreur : {str(e)}")

# Route pour enregistrer le scénario validé
@app.route('/enregistrer', methods=['POST'])
def enregistrer_scenario():
    try:
        scenario_json = request.form.get("scenario", "{}")
        scenario_dict = json.loads(scenario_json)

        fichier_scenario = os.path.join(SCENARIOS_DIR, "scenario_sauvegarde.json")
        with open(fichier_scenario, "w", encoding="utf-8") as f:
            json.dump(scenario_dict, f, indent=4, ensure_ascii=False)

        return send_file(fichier_scenario, as_attachment=True, download_name="scenario_sauvegarde.json")
    except Exception as e:
        return render_template('index.html', error=str(e)), 500

# Route principale
@app.route('/')
def index():
    return render_template('index1.html')

# Lancer l'application Flask sur Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Port dynamique pour Render
    app.run(host="0.0.0.0", port=port, debug=True)
