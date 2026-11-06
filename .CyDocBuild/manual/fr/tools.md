---
id: tools
title: Outils MCP et compatibilité
description: Transports MCP, contrats des outils, ressources et noms compatibles.
section: Références / API publique
order: 17
revision: 2
sourceRevision: 2
---


## Opérations MCP {#content}


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


Les outils sont des opérations du protocole MCP. Leurs signatures de forme Python décrivent les arguments transmis ; ce ne sont pas des fonctions importables depuis un module. Les sous-pages détaillent paramètres et retours ; les [contrats de données](doc:data-contracts#content) décrivent les fiches Skill et image.

Lisez la portée, recherchez des résultats synthétiques puis consultez la fiche choisie. Après un conflit de version, relisez la fiche et conciliez les modifications avant de réessayer. Les fiches absentes, non publiées ou hors portée ne sont pas exposées.

## Exemple d’appel court {#example}

Dans une session MCP établie, les arguments d’une requête `tools/call` peuvent être :

```json
{"name":"search_skills","arguments":{"query":"github","limit":5}}
```


## Noms compatibles {#compatibility}

Les anciens clients peuvent continuer à appeler les outils suivants. Paramètres et résultats correspondent aux opérations Skill actuelles ; `method_id` correspond à `skill_id`, et `method` à `skill`.

```python
search_methods(query: str = '', category: str = '', limit: int = 10, offset: int = 0) -> dict[str, Any]
get_method(method_id: str) -> dict[str, Any]
create_method(method: Method) -> dict[str, Any]
update_method(method_id: str, expected_version: int, method: Method) -> dict[str, Any]
```

## Ressources et prompts {#resources}

`skills://context` et `methodes://context` retournent le même contexte de connexion sous forme de texte JSON. Le prompt `apply_skills(task: str)` retourne des consignes liées à la tâche ; `appliquer_methodes(task: str)` est son équivalent français historique. Ces prompts n’exécutent pas eux-mêmes d’outils et ne modifient aucune fiche.

## Découverte HTTP publique {#http-discovery}

Ces routes en lecture seule appartiennent à l’application FastAPI locale du module `skills.server`. Elles exigent le serveur lancé, sans jeton de connexion. Elles ne retournent aucun contenu personnel de bibliothèque. Les routes d’administration sous `/api` sont destinées à l’interface applicative authentifiée.

| Requête | Paramètres | Réponse |
| --- | --- | --- |
| `GET /health` | Aucun | JSON : `app`, `status`, `version`, `packaged`, `tray`. L’identifiant compatible `app` reste `methodes` ; `status` vaut `ok`. |
| `GET /mcp-info` | Aucun | JSON : nom/version, transport/URL, jeton exigé ou non, clients compatibles, procédure et liens vers les guides. Certains textes explicatifs historiques restent en français. |
| `GET /mcp-guide` | `client=all`, `lang=en` | Pièce jointe Markdown pour le client et la langue choisis. Les valeurs de client sont celles de `get_setup_guide` ; la langue vaut `en` ou `fr`. Une valeur de requête invalide retourne HTTP 422. |

```bash
curl http://127.0.0.1:8765/health
```

Adaptez le port pour une instance personnalisée configurée volontairement. Ouvrir `/mcp` dans un navigateur n’établit pas de session MCP ; suivez les [étapes de connexion](doc:mcp#content) de votre client.
