---
id: mcp
title: Connecter Codex, Claude Desktop ou OpenCode
description: Connecter un client compatible à votre bibliothèque MCP locale.
section: Connexions
order: 7
revision: 2
sourceRevision: 2
---


## Configurer et tester une connexion {#content}


1. Démarrez CyAICodex et ouvrez Connexions > Configurer et tester.
2. Choisissez l’accès avec jeton, ou l’accès local sans jeton déjà activé volontairement. Choisissez portée, globaux et écriture lorsque disponibles.
3. Dans la carte du client, cliquez sur Configurer et tester. Les configurations reconnues sont sauvegardées et les autres serveurs préservés. Un fichier invalide ou une entrée homonyme étrangère n’est pas écrasé.
4. Reconnectez CyAICodex dans le client ou redémarrez ce client. Un client ouvert peut conserver une ancienne liste d’outils.
5. Utilisez Tester seulement puis demandez à l’IA get_context, search_skills et get_skill pour vérifier ce qu’elle lit réellement.

## Étapes de connexion MCP {#diagram-1}

```diagram
{"type": "flow", "title": "Étapes de connexion MCP", "nodes": [{"id": "n0", "label": "Serveur lancé", "x": 0, "y": 20, "width": 240}, {"id": "n1", "label": "Client configuré", "x": 280, "y": 20, "width": 240}, {"id": "n2", "label": "Connexion MCP testée", "x": 560, "y": 20, "width": 240}], "edges": [{"from": "n0", "to": "n1"}, {"from": "n1", "to": "n2"}]}
```

- **Serveur lancé** — CyAICodex répond localement.
- **Client configuré** — Une entrée CyAICodex existe chez le client.
- **Connexion MCP testée** — Initialize, tools/list et get_context ont abouti.

Le même CyAICodex.exe gère l’interface et --mcp-stdio. Les clients stdio peuvent démarrer le serveur partagé à la demande. Fermer un client ne ferme pas le serveur indépendant de l’icône. Aucune passerelle exécutable distincte n’est nécessaire.

```callout
{"type": "tip", "title": "À retenir", "body": "L’accès à la bibliothèque ne connecte pas un compte d’assistant. Le paramétrage MCP et la connexion du fournisseur de l’assistant intégré sont distincts."}
```
