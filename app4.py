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

# Définir le prompt pour guider le LLM
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "Tu es un assistant chargé de créer des scénarios immersifs pour trois niveaux distincts :\n"
                   "- Niveau Débutant : Formation guidée avec aides visuelles et auditives.\n"
                   "- Niveau Intermédiaire : Réduction des aides avec des distractions.\n"
                   "- Niveau Avancé : Limitation de temps et tâches simultanées."),
        ("user", "{requete}\nCrée un scénario adapté pour le niveau suivant : {niveau}.")
    ]
)

# Fonction pour éviter les répétitions
def nettoyer_texte(texte):
    """Nettoie les répétitions inutiles dans un texte."""
    lignes = texte.splitlines()
    texte_nettoye = []
    for ligne in lignes:
        if ligne not in texte_nettoye:  # Élimine les doublons
            texte_nettoye.append(ligne)
    return "\n".join(texte_nettoye)

# Génération de scénario
def generer_scenario_pour_niveau(requete, niveau):
    """Génère un scénario spécifique à un niveau donné."""
    try:
        query = prompt_template.invoke({"requete": requete, "niveau": niveau})
        response = llm.stream(query.messages)  # Récupération correcte du prompt
        scenario = "".join([chunk.content for chunk in response])
        return nettoyer_texte(scenario)  # Nettoie les répétitions
    except Exception as e:
        print(f"Erreur lors de la génération du scénario pour le niveau {niveau} : {e}")
        return None

# Génération structurée pour tous les niveaux
def structurer_scenarios(requete):
    """Génère des scénarios pour tous les niveaux et les organise."""
    niveaux = ["Débutant", "Intermédiaire", "Avancé"]
    scenarios = {}
    for niveau in niveaux:
        scenario = generer_scenario_pour_niveau(requete, niveau)
        scenarios[niveau] = {
            "description": f"Scénario adapté pour le niveau {niveau}",
            "scenario": scenario if scenario else "Erreur lors de la génération."
        }
    return scenarios

# Route pour générer des scénarios par niveaux (via formulaire HTML)
@app.route('/generer_niveaux', methods=['POST'])
def generer_scenarios_niveaux():
    requete = request.form.get("requete", "")
    scenarios = structurer_scenarios(requete)
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

@app.route('/api/generer_niveaux', methods=['POST'])
def api_generer_scenarios_niveaux():
    requete = request.json.get("requete", "")  # Utilisation de JSON au lieu de form
    scenarios = structurer_scenarios(requete)
    return jsonify(scenarios)

# Route principale
@app.route('/')
def index():
    return render_template('index1.html')

# Lancer l'application Flask sur Render
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Port dynamique pour Render
    app.run(host="0.0.0.0", port=port, debug=True)