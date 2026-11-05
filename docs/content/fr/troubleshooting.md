---
id: troubleshooting
title: Dépannage
description: Le journal rotatif est cyaicodex.log dans data. L’installation écrit installation.log à côté de ce dossier. Les anciennes versions pouvaient utiliser methodes.log. Transmettez seulement l’erreur utile expurgée et la version, jamais bibliothèque complète, identifiants ou jetons.
section: Guide utilisateur
order: 16
revision: 1
sourceRevision: 1
---

## Dépannage {#content}


| Symptôme | Vérification |
| --- | --- |
| Page inaccessible | Démarrez CyAICodex, vérifiez l’icône et le PC éveillé. Un autre logiciel peut occuper le port 8765. |
| Rouvrir depuis l’icône demandé | Utilisez icône ou raccourci pour établir la session d’administration. Ne partagez pas le lien. |
| Client configuré mais outils absents | Reconnectez MCP ou redémarrez le client puis Tester seulement. La configuration enregistrée ne prouve pas son rechargement. |
| Jeton absent ou révoqué | Reconfigurez la connexion prévue ; ne collez pas de jeton dans le dépannage. |
| Skill ou image absent | Vérifiez Publié, portée, globaux, filtres et get_context. |
| Conflit d’enregistrement | Rechargez et comparez ; n’écrasez pas aveuglément. |
| Client non détecté | Vérifiez installation, connexion native et chemin. Application graphique et CLI peuvent être distincts. |
| Ollama sans modèles | Démarrez Ollama et installez un modèle séparément, puis Vérifier et sélectionnez-le. |
| Image refusée | Vérifiez vision du modèle et de l’adaptateur, format et taille. |
| Mise à jour privée GitHub en échec | Vérifiez Git local ou jeton limité au dépôt, réseau et release disponible. |
| Pas de lancement avant connexion Windows | C’est un démarrage à l’ouverture de session, pas un service système avant connexion. |
| Image du manuel absente | Conservez _internal/help intact puis réparez ou réinstallez ; tous les fichiers CyDoc exportés doivent rester ensemble. |

Le journal rotatif est cyaicodex.log dans data. L’installation écrit installation.log à côté de ce dossier. Les anciennes versions pouvaient utiliser methodes.log. Transmettez seulement l’erreur utile expurgée et la version, jamais bibliothèque complète, identifiants ou jetons.

```callout
{"type": "tip", "title": "À retenir", "body": "Gardez data et les sauvegardes après un échec de lancement ou de mise à jour. Diagnostiquez ; ne supprimez pas la bibliothèque pour résoudre une connexion."}
```
