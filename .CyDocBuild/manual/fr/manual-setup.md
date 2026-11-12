---
id: manual-setup
title: Configurer un autre client MCP
description: Configurer un autre client MCP et obtenir une aide adaptée à ce client.
section: Connexions
order: 8
revision: 3
sourceRevision: 3
parent: mcp
---


## Utiliser une configuration client générée {#content}


1. Créez une connexion nommée dans Connexions avec la portée et les droits requis.
2. Copiez la configuration générée tant que le jeton est visible. Choisissez le format du client et suivez ses réglages MCP.
3. Pour Streamable HTTP, utilisez l’adresse locale /mcp et le jeton Bearer avec le serveur lancé. Pour stdio, utilisez la commande et les arguments générés.
4. Reconnectez le client et effectuez un vrai test MCP. Ouvrir /mcp dans le navigateur n’est pas un test du protocole.

Sous Informations à transmettre à une autre IA, téléchargez le guide Markdown français ou anglais et joignez-le à la conversation. Une IA connectée peut appeler get_setup_guide(client, language). Claude Desktop et Claude Code sont distincts ; la configuration automatique couvre Codex, Claude Desktop et OpenCode.

La découverte locale passe par /mcp-info et le guide par /mcp-guide. Ils ne contiennent ni jeton ni fiche personnelle. Le Markdown décrit les étapes ; un utilisateur ou agent capable et autorisé doit encore configurer le client.


```callout
{"type": "tip", "title": "À retenir", "body": "Une IA cloud ne peut pas joindre directement le localhost de ce PC. Utilisez un client local ou un environnement d’exécution local compatible ; n’exposez pas le serveur sur Internet pour contourner cette limite."}
```

## Installer le Skill Agent portable {#agent-skill}

CyAICodex fournit un même `cyaicodex/SKILL.md` standard pour Codex, Claude Code et les clients compatibles Agent Skills. Il indique au client quand et comment consulter cette bibliothèque MCP. Il n’installe pas l’application, ne connecte pas MCP et ne copie pas vos fiches personnelles dans le client.

[Télécharger le ZIP du Skill](https://mrmybal.github.io/CyAICodex/AgentSkills/CyAICodex-Skill.zip). Les compilations depuis les sources placent aussi le ZIP dans `Documentation/AgentSkills/CyAICodex-Skill.zip` ; les versions déjà installées peuvent utiliser le téléchargement séparé.

- **Codex :** extrayez l’archive et copiez son dossier `cyaicodex` dans `~/.agents/skills/` (tous les projets) ou dans `.agents/skills/` du projet. Un client ancien ou personnalisé qui lit `~/.codex/skills/` peut utiliser le même dossier à cet endroit à la place.
- **Claude Code :** copiez le même dossier dans `~/.claude/skills/` ou dans `.claude/skills/` du projet.
- **Application Claude / claude.ai :** importez et activez le ZIP dans Personnaliser > Skills si votre offre et votre espace autorisent les Skills personnalisés. Un environnement cloud ne peut toujours pas joindre directement le localhost du PC.

Actualisez les Skills du client ou démarrez une nouvelle session, puis appelez `$cyaicodex` dans Codex ou `/cyaicodex` dans Claude Code. Vérifiez un véritable appel `get_context`. La sélection automatique dépend du client et de la tâche ; ajoutez une consigne permanente si chaque tâche doit consulter la bibliothèque.

Depuis les sources, PowerShell 7 peut installer pour les deux clients locaux avec `pwsh -File .\integrations\skills\Install-Skill.ps1 -Client all`. Les personnalisations existantes sont préservées sans demande explicite de mise à jour. Les consignes communes sont en anglais ; l’agent répond dans votre langue. [Instructions d’installation détaillées](https://github.com/MrMybal/CyAICodex/blob/main/integrations/skills/README.fr.md).
