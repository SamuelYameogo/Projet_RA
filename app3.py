from flask import Flask, render_template, request, jsonify
import json
import os
from apikey import apikey
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Initialisation de l'application Flask
app = Flask(__name__, static_folder='static')

# Dossier où stocker les scénarios validés
SCENARIOS_DIR = "scenarios"
os.makedirs(SCENARIOS_DIR, exist_ok=True)

# Clé API Groq
GROQ_API_KEY = apikey
llm = ChatGroq(model_name="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)

# Définition des prompts
prompt_validation = ChatPromptTemplate.from_messages([
    ("system", "Tu es un assistant chargé de vérifier la validité d'une étape donnée dans un scénario. "
               "Analyse si l'étape correspond à une des consignes ou étapes de validation listées. "
               "Réponds uniquement avec 'validé' si l'étape est correcte, sinon avec 'non validé'."),
    ("user", "Scénario : {scenario}\nÉtape à valider : {etape}")
])

# Route principale
@app.route('/')
def index():
    return render_template('index.html')

# Route pour valider une étape avec le LLM
@app.route('/valider', methods=['POST'])
def valider_etape():
    try:
        data = request.get_json()
        scenario_json = data.get("scenario", "{}")
        etape_validee = data.get("etape", "")

        # Vérifier si le JSON est valide
        try:
            scenario_dict = json.loads(scenario_json)
        except json.JSONDecodeError:
            return jsonify({"validation": "Erreur: Le scénario fourni n'est pas un JSON valide."})

        # Vérifier avec le LLM
        scenario_str = json.dumps(scenario_dict, ensure_ascii=False, indent=4)
        query = prompt_validation.format(scenario=scenario_str, etape=etape_validee)
        response = llm.invoke(query)
        validation_result = response.content.strip().lower()

        if validation_result == "validé":
            if "etapes_validation" in scenario_dict and etape_validee in scenario_dict["etapes_validation"]:
                scenario_dict["etapes_validation"][etape_validee] = True
                validation_result = "Validé"
            else:
                validation_result = "Étape non trouvée dans le scénario"
        else:
            validation_result = "Non validé"

        return jsonify({"validation": validation_result, "scenario": json.dumps(scenario_dict, indent=4, ensure_ascii=False)})

    except Exception as e:
        return jsonify({"validation": f"Erreur : {str(e)}"})

# Route pour enregistrer le scénario validé
@app.route('/enregistrer', methods=['POST'])
def enregistrer_scenario():
    try:
        data = request.json
        scenario_json = json.loads(data["scenario"])
        fichier_scenario = os.path.join(SCENARIOS_DIR, "scenario_sauvegarde.json")
        with open(fichier_scenario, "w", encoding="utf-8") as f:
            json.dump(scenario_json, f, indent=4, ensure_ascii=False)
        return jsonify({"message": "Scénario enregistré avec succès !"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lancer l'application Flask
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

