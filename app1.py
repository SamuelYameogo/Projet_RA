from flask import Flask, render_template, request, jsonify
import os
from apikey import apikey
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Initialisation de l'application Flask
app = Flask(__name__) 

# Configuration de la clé API pour ChatGroq
GROQ_API_KEY = apikey
llm_groq = ChatGroq(model_name="llama-3.1-70b-versatile", api_key=GROQ_API_KEY)

# Modèle de prompt
prompt_groq = ChatPromptTemplate.from_messages(
    [("system", "Tu es un assistant chargé de créer des scénarios de crise ou d'accident à partir des messages de l'utilisateur. Ne fais pas de secourisme, mais développe la scène de l'accident. Fais-le de manière synthétique."),
     ("user", "{input}")]
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_scenario():
    user_input = request.form.get('user_input')
    
    # Validation de l'entrée utilisateur
    if not user_input or len(user_input.split()) > 20:
        return jsonify({'error': 'Votre requête doit contenir au maximum 20 mots.'})

    try:
        # Génération de scénario avec ChatGroq
        query = prompt_groq.format(input=user_input)
        response = llm_groq.stream(query)
        
        scenario = ""
        for chunk in response:
            scenario += chunk.content

        return jsonify({'scenario': scenario})

    except Exception as e:
        return jsonify({'error': f"Erreur lors de la génération du scénario : {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
