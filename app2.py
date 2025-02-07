from flask import Flask, render_template, request, jsonify
import json
import os
from apikey import apikey

# Initialisation de l'application Flask
app = Flask(__name__, static_folder='static')

# Dossier où stocker les scénarios validés
SCENARIOS_DIR = "scenarios"
os.makedirs(SCENARIOS_DIR, exist_ok=True)

# Route principale pour afficher la page HTML
@app.route('/')
def index():
    return render_template('index.html')

# Route pour valider une étape sans utiliser le LLM
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

        # Vérifier si l'étape existe dans le dictionnaire des validations et la passer à True
        if "etapes_validation" in scenario_dict and etape_validee in scenario_dict["etapes_validation"]:
            scenario_dict["etapes_validation"][etape_validee] = True
            validation_result = "Validé"
        else:
            validation_result = "Étape non trouvée dans le scénario"

        return jsonify({"validation": validation_result, "scenario": json.dumps(scenario_dict, indent=4, ensure_ascii=False)})

    except Exception as e:
        return jsonify({"validation": f"Erreur : {str(e)}"})

# Route pour enregistrer le scénario validé
@app.route('/enregistrer', methods=['POST'])
def enregistrer_scenario():
    try:
        data = request.json
        scenario_json = json.loads(data["scenario"])  # Convertir en dictionnaire Python

        # Définir le nom du fichier
        fichier_scenario = os.path.join(SCENARIOS_DIR, "scenario_sauvegarde.json")

        # Sauvegarder dans un fichier JSON
        with open(fichier_scenario, "w", encoding="utf-8") as f:
            json.dump(scenario_json, f, indent=4, ensure_ascii=False)

        return jsonify({"message": "Scénario enregistré avec succès !"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lancer l'application Flask
if __name__ == '__main__':
    app.run(debug=True)
