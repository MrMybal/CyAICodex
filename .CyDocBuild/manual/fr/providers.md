---
id: providers
title: Référence des fournisseurs et connecteurs
description: Choisir entre clients locaux, modèles locaux et fournisseurs API.
section: Assistant
order: 11
revision: 2
sourceRevision: 2
parent: assistant
---


## Choisir votre fournisseur {#content}


Installez le client ou démarrez le serveur du fournisseur d’abord. Un chemin personnalisé dans Paramètres peut remplacer la détection. Vérifier la disponibilité, charger les modèles et tester une réponse sont des actions distinctes.

| Fournisseur | Prérequis et réglage | Images |
| --- | --- | --- |
| Codex | Client local ; vérifier le compte et se connecter depuis Connexions. | Selon modèle |
| Claude Code | Client local et connexion native au compte. | Selon modèle |
| OpenCode | Client avec fournisseur configuré ; modèle au format fournisseur/modèle. | Selon modèle |
| Ollama | Serveur local, par défaut http://127.0.0.1:11434 ; installer un modèle séparément. | Modèle avec vision requis |
| OpenAI API | Clé API distincte et identifiant exact du modèle. | Selon modèle |
| Claude API | Clé API Anthropic distincte et identifiant exact du modèle. | Selon modèle |
| Antigravity | CLI agy détecté et compte connecté. | Non |
| Command Code | CLI cmdc ou command-code détecté et compte. | Non |
| CodeBuddy | CLI codebuddy ou cbc détecté et compte. | Non |
| OpenRouter | Clé API OpenRouter et identifiant du modèle. | Selon modèle |
| LM Studio | Serveur local démarré ; adresse par défaut http://127.0.0.1:1234/v1. | Selon modèle |

## Connecteurs supplémentaires {#additional-connectors}

1. Dans Paramètres > Connecteurs supplémentaires, enregistrez chemin du client ou adresse serveur et identifiants si nécessaire.
2. Cliquez sur Vérifier puis Charger les modèles si disponible. Choisissez un modèle retourné ou saisissez un identifiant compatible.
3. Testez une réponse si souhaité. Ce petit message peut consommer du quota et ne transmet pas les Skills.
4. Dans Assistant, sélectionnez ce fournisseur et ce modèle pour la vraie demande.

Catalogues et droits des comptes peuvent changer. La disponibilité ne prouve pas l’accès à tous les modèles. Ces boutons n’installent rien. LM Studio exige une adresse HTTP locale terminée par /v1 ; Ollama exige aussi une adresse locale.

Antigravity et Command Code utilisent leurs modes plan et intégrations natifs ; CyAICodex ne relaie pas les approbations. L’adaptateur CodeBuddy désactive les outils. Les adaptateurs CLI n’ont pas tous les mêmes capacités d’exécution.
