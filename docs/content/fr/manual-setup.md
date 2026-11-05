---
id: manual-setup
title: Autres clients et guides pour les IA
description: Sous Informations à transmettre à une autre IA, téléchargez le guide Markdown français ou anglais et joignez-le à la conversation. Une IA connectée peut appeler get_setup_guide(client, language). Claude Desktop et Claude Code sont distincts ; la configuration automatique couvre Codex, Claude Desktop et OpenCode.
section: Guide utilisateur
order: 8
revision: 1
sourceRevision: 1
---

## Autres clients et guides pour les IA {#content}


1. Créez une connexion nommée dans Connexions avec la portée et les droits requis.
2. Copiez la configuration générée tant que le jeton est visible. Choisissez le format du client et suivez ses réglages MCP.
3. Pour Streamable HTTP, utilisez l’adresse locale /mcp et le jeton Bearer avec le serveur lancé. Pour stdio, utilisez la commande et les arguments générés.
4. Reconnectez le client et effectuez un vrai test MCP. Ouvrir /mcp dans le navigateur n’est pas un test du protocole.

Sous Informations à transmettre à une autre IA, téléchargez le guide Markdown français ou anglais et joignez-le à la conversation. Une IA connectée peut appeler get_setup_guide(client, language). Claude Desktop et Claude Code sont distincts ; la configuration automatique couvre Codex, Claude Desktop et OpenCode.

La découverte locale passe par /mcp-info et le guide par /mcp-guide. Ils ne contiennent ni jeton ni fiche personnelle. Le Markdown décrit les étapes ; un utilisateur ou agent capable et autorisé doit encore configurer le client.

```text
Au début de chaque tâche, appelle get_context, puis search_skills et get_skill pour les pratiques pertinentes. Respecte la portée de cette connexion. Crée ou modifie un skill seulement à ma demande, avec expected_version pour les modifications.
```

```callout
{"type": "tip", "title": "À retenir", "body": "Une IA cloud ne peut pas joindre directement le localhost de ce PC. Utilisez un client local ou un environnement d’exécution local compatible ; n’exposez pas le serveur sur Internet pour contourner cette limite."}
```
