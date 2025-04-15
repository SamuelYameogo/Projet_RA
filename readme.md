# 🚨 FIFA 2030 – Simulateur de Crises Sanitaires (Secourisme)

**Composante IA d'un projet de réalité virtuelle (RV et RA) la formation interactive des agents de secours**  
*Conçue pour les environnements à forte affluence (stades, gares) durant la FIFA 2030 au Maroc.*

---

## 🧠 Présentation du Projet

Ce projet vise à enrichir une **expérience de simulation en Réalité Augmentée (RA)** développée sous **Unity**, par l’ajout d’une **composante IA** capable de :

- Générer dynamiquement des **scénarios de secours réalistes**,
- Adapter le niveau de difficulté aux profils des apprenants,
- Suivre et valider **les étapes critiques des gestes de premiers secours**,
- Fournir un retour en temps réel, via l’interface RA.

L’objectif est de proposer une **formation immersive**, interactive et personnalisée pour les futurs intervenants sur le terrain, en particulier dans le cadre de grands événements comme la Coupe du Monde 2030.

> 🎮 La partie visuelle (simulation et interaction RA) est développée sous Unity par un second membre de l’équipe, en se basant sur les scénarios textuels générés par l’IA.

---

## 🗂️ Structure du Projet 
```bash
.
├── app/                       # Serveurs Flask pour génération et validation
│   ├── app2.py               # Version simple, uniquement validation 
│   ├── app5.py               # Scénarios IA + consignes guidées
│   ├── app6.py               # Version finale : fusion app2 et app5 améliorée
│   └── apikey.py             # Contient votre clé API Groq
├── scripts/                  # Tests de modèles LLM
│   ├── llama1-8.py           # Générations successives LLaMA
│   ├── gemma.py              # Test Gemma
│   ├── mistral.py            # Test Mistral
│   └── ...
├── scenarios/                # Scénarios JSON multi-niveaux
├── static/                   # Interface web (formulaires, assets)
├── requirements.txt          # Dépendances Python
├── Procfile                  # Déploiement Render
├── start.sh                  # Script de démarrage Render
├── req.txt                   # Modules/ Déploiement Render
└── .github/workflows/        # Workflow de veille du site
```



## 🧠 Intégration IA : Objectifs et Développement

L’intégration de l’IA dans le projet vise deux grands objectifs complémentaires :

1. **Génération de scénarios textuels de crises sanitaires réalistes**  
   Grâce aux modèles de langage (LLM), les scénarios sont produits dynamiquement à partir de prompts décrivant des contextes comme une gare ou un stade lors d’un match FIFA. Ils sont ensuite enrichis avec des consignes claires, plusieurs niveaux de difficulté, et des étapes de validation des gestes de secours.

2. **Guidage et validation interactive**  
   L’apprenant est assisté par l’IA tout au long de son intervention via un système de validation dynamique. Chaque action est vérifiée et contextualisée par rapport au niveau de difficulté et au scénario actif. Unity interagit avec l’API Flask pour envoyer les actions réalisées par l’utilisateur, qui sont ensuite validées par le backend IA.

---

## 🧩 Étapes de Développement IA

Voici les grandes étapes qui ont structuré l’intégration IA dans le projet :

- ✅ **Initialisation de l’environnement Python de travail**  
  Création d’un environnement virtuel, mise en place d’une structure modulaire, intégration de Flask pour servir les modèles.

- 🧪 **Exploration de LangChain et tests de modèles LLM**  
  Test des modèles LLaMA, Gemma, Mistral, ChatGPT, Anthropic. Choix de **LLaMA** pour sa performance et sa libre utilisation.

- 🧱 **Génération initiale de scénarios simples**  
  Codés sous forme de fichiers Python (`llama1.py`, `llama2.py`...), les premiers scénarios intègrent des consignes figées.

- 🔀 **Ajout de règles d’interaction prédéfinies**  
  Les fichiers llama2 et llama3 présentent l'intégration de règles précises et structurées par niveau de scénario.

- 🎚️ **Multi-niveaux et profondeur scénaristique (llama4+)**  
  Génération de consignes plus détaillées et validation progressive selon l’étape de l’intervention (ex : Alerter → Isoler → Traiter).

- 🧠 **Validation dynamique (llama7-8)**  
  Capacité à réagir en fonction des actions reçues par l’interface Unity : analyse de la pertinence de l’action, retour en temps réel.

- 📁 **Création d’une base de scénarios**  
  Stockage dans `/scenarios` de dizaines de cas d’entraînement générés avec des consignes précises et structurés en JSON.


## 📚 Exemple de Scénario
```json
{
"Avancé": {
        "description": "Scénario adapté pour le niveau Avancé",
        "scenario": "**Scénario : Malaise cardiaque sur un terrain de football - Niveau Avancé**\n\n**Introduction :**\nVous êtes un infirmier diplômé d'État (IDE) qui travaille sur un terrain de football pendant un match important. Soudain, un joueur s'effondre après une course intense. Les joueurs et les spectateurs sont paniqués. Vous devez agir rapidement pour sauver la vie du joueur.",
        "consignes": [
            "Identifier les symptômes du malaise cardiaque et prendre les mesures appropriées.",
            "Gérer les distractions et interruptions tout en restant concentré.",
            "Optimiser le temps d'intervention pour effectuer chaque tâche essentielle.",
            "Effectuer une réanimation cardiopulmonaire (RCP) en cas d'absence de pouls."
        ],
        "etapes_validation": {
            "Symptômes correctement identifiés": false,
            "Appel aux secours effectué": false,
            "RCP effectuée si nécessaire": false,
            "Gestion efficace des distractions": false,
            "Temps d'intervention optimisé": false
        }
    }
}
```

## 🧪 Tests

Plusieurs moyens sont disponibles pour tester la partie IA localement ou en interaction avec l’environnement Unity :

### ✅ Simulation locale (tests IA purs)

Clonez ce dépôt, puis lancez l’un des fichiers suivants selon votre besoin :

```bash
git clone https://github.com/votre-nom-utilisateur/projet-ra.git
cd projet-ra
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

- **Tests de génération de scénarios** :
  Utilisez les fichiers `scripts/llama1.py` à `llama8.py` pour exécuter localement les différentes étapes de création de scénarios avec LLaMA.

- **Simulation complète avec app Flask** :  
  Le fichier `app5.py` permet de lancer une version plus avancée du backend IA qui génère des scénarios avec consignes et étapes validées.
  
  ```bash
  python app/app5.py
  ```

  Accédez ensuite à l’interface sur `http://localhost:5000`.

### 🔁 Intégration avec Unity (ou tests via C#)

Les fichiers `app2.py` et `app6.py` sont pensés pour recevoir des requêtes HTTP depuis Unity (par exemple via `UnityWebRequest`) :

- `app2.py` : version intermédiaire pour la **validation de scénarios sans IA**
- `app6.py` : version complète, **validation dynamique + retour contextuel**

Exemple d'appel HTTP côté C# dans Unity :
```csharp
UnityWebRequest request = UnityWebRequest.Post("https://projet-ra.onrender.com/valider", bodyData);
```

> Pour une première intégration entre la **composante RA** (Unity) et l’**IA** (Flask), vous pouvez tester en ligne via le site déployé :  
> 🌐 [https://projet-ra.onrender.com](https://projet-ra.onrender.com)
