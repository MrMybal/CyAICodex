---
id: tools
title: Outils MCP et compatibilité
description: search_methods, get_method, create_method et update_method restent compatibles. skills://context et methodes://context exposent la portée. apply_skills est le prompt actuel ; appliquer_methodes reste compatible.
section: Guide utilisateur
order: 17
revision: 1
sourceRevision: 1
---

## Outils MCP et compatibilité {#content}


| Outil | Usage |
| --- | --- |
| get_context | Lire portée, globaux et droit d’écriture. |
| search_skills / get_skill | Trouver les Skills publiés et lire contenu et version. |
| create_skill / update_skill | Écrire si autorisé ; expected_version requis pour modifier. |
| search_images / get_image / view_image | Trouver les images, lire leurs règles et un aperçu. |
| import_image | Ajouter une image depuis un chemin absolu local ou base64 avec description. |
| update_image | Modifier les règles avec expected_version ; l’original reste intact. |
| get_setup_guide | Consignes de connexion en anglais ou français. |

search_methods, get_method, create_method et update_method restent compatibles. skills://context et methodes://context exposent la portée. apply_skills est le prompt actuel ; appliquer_methodes reste compatible.

Le transport utilise Streamable HTTP sur /mcp ou la commande stdio générée. Port standard : 8765. Les options sources et CLI --port, --data-dir, --no-open, --headless, --mcp-stdio et --stop servent aux instances personnalisées gérées volontairement.

```callout
{"type": "tip", "title": "À retenir", "body": "MCP rend les ressources accessibles sans obliger un modèle à les lire. Inscrivez get_context → search_skills → get_skill dans ses instructions. Droits et contexte continuent de s’appliquer."}
```
