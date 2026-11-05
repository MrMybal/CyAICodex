---
id: permissions
title: Autorisations, jetons et confidentialité
description: Modifiez l’écriture d’une connexion dans Connexions. Le jeton est affiché une fois à sa création ; seule son empreinte est conservée. Une révocation impose une nouvelle configuration. Ne collez jamais de secrets dans des conversations, captures ou rapports publics.
section: Guide utilisateur
order: 9
revision: 1
sourceRevision: 1
---

## Autorisations, jetons et confidentialité {#content}


| Réglage | Effet |
| --- | --- |
| Lecture seule | Lire les ressources publiées accessibles ; aucune création ni modification. |
| Écriture | Créer et modifier les ressources accessibles, globales comprises si incluses. |
| Révoquer | Invalider le jeton de cette connexion. |
| Accès local sans jeton | Permettre aux processus locaux la portée et les droits configurés sans jeton Bearer. |
| Écriture par défaut | Précocher l’écriture pour les nouvelles connexions avec jeton ; les existantes ne changent pas. |

Modifiez l’écriture d’une connexion dans Connexions. Le jeton est affiché une fois à sa création ; seule son empreinte est conservée. Une révocation impose une nouvelle configuration. Ne collez jamais de secrets dans des conversations, captures ou rapports publics.

Paramètres > Autorisations MCP définit contexte, globaux et écriture de l’accès sans jeton. Ce mode ne supprime ni la séparation des projets ni la protection distincte de l’administration. Les demandes d’approbation des clients IA se règlent dans ces clients, pas avec cette option.

```callout
{"type": "tip", "title": "À retenir", "body": "Stockage local ne signifie pas requête d’assistant locale. Envoyer un message transmet conversation et références au fournisseur choisi. Ollama ou LM Studio peut fonctionner localement ; les fournisseurs cloud reçoivent les requêtes selon leurs règles."}
```
