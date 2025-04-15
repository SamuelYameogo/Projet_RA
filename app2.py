"""
API Flask minimaliste pour valider/enregistrer des scénarios JSON

Fonctionnalités :
- Validation d'étapes dans un scénario structuré
- Sauvegarde locale en JSON
- Téléchargement du fichier
- Compatible CORS pour intégration cross-origin (ex: Unity)

Routes :
- POST /valider : Met à jour le statut des étapes
- GET /enregistrer : Télécharge le scénario validé

Usage typique :
1. Envoyer un scénario JSON avec étapes à valider
2. Récupérer le fichier final après validation
"""



from flask import Flask, render_template, jsonify, send_from_directory, request
import json
import os
from flask_cors import CORS

# Initialisation de l'application Flask
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Active CORS pour permettre les requêtes depuis Unity

# Dossier où stocker les scénarios validés
SCENARIOS_DIR = "scenarios"
os.makedirs(SCENARIOS_DIR, exist_ok=True)

# Fichier où sera sauvegardé le scénario validé
FICHIER_SCENARIO = os.path.join(SCENARIOS_DIR, "scenario_sauvegarde.json")

# Route principale pour afficher la page HTML
@app.route('/')
def index():
    return render_template('index.html')

# Route pour valider plusieurs étapes à la fois et enregistrer le scénario
@app.route('/valider', methods=['POST'])
def valider_etapes():
    try:
        data = request.get_json()
        scenario_json = data.get("scenario", "{}")
        etapes_validees = data.get("etapes", [])

        # Vérifier si le JSON est valide
        try:
            scenario_dict = json.loads(scenario_json)
        except json.JSONDecodeError:
            return jsonify({"error": "Le scénario fourni n'est pas un JSON valide."}), 400

        # Vérifier si la structure du scénario contient "etapes_validation"
        if "etapes_validation" not in scenario_dict:
            return jsonify({"error": "Structure du scénario invalide. 'etapes_validation' manquant."}), 400

        # Valider chaque étape
        validation_result = {}
        for etape in etapes_validees:
            if etape in scenario_dict["etapes_validation"]:
                scenario_dict["etapes_validation"][etape] = True  # Mettre à jour à True
                validation_result[etape] = "Validé ✅"
            else:
                validation_result[etape] = "Non trouvée ❌"

        # Enregistrer le scénario validé dans un fichier
        with open(FICHIER_SCENARIO, "w", encoding="utf-8") as f:
            json.dump(scenario_dict, f, indent=4, ensure_ascii=False)

        return jsonify({
            "message": "Scénario validé et enregistré.",
            "validation": validation_result,
            "scenario": scenario_dict  # Retourner directement le scénario mis à jour
        })

    except Exception as e:
        return jsonify({"error": f"Erreur : {str(e)}"}), 500

# Route pour télécharger le scénario validé
@app.route('/enregistrer', methods=['GET'])
def enregistrer_et_telecharger():
    try:
        return send_from_directory(SCENARIOS_DIR, "scenario_sauvegarde.json", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Lancer l'application Flask
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
