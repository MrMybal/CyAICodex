---
id: data-contracts
title: Contrats des fiches Skill et image
description: Champs, règles de portée et format des fiches avec versions.
section: Références / API publique
parent: tools
order: 220
revision: 1
sourceRevision: 1
---

## Règles communes des fiches {#content}

Les schémas des outils MCP exposent `Method` (nom conservé pour une fiche Skill) et `ImageDescription`. Leurs définitions Python utilisent Pydantic dans `skills.store` et `skills.images`. Les clients MCP transmettent des objets JSON ; ils n’importent pas ces classes internes.

| Champ | Type / défaut | Signification |
| --- | --- | --- |
| `title` | `str`, obligatoire | Non vide, de 1 à 160 caractères. |
| `category` | `str` | De 1 à 80 caractères ; les valeurs historiques par défaut sont `Général` pour les Skills et `Référence` pour les images. Indiquez votre propre libellé pour choisir la langue. |
| `tags` | `list[str]`, `[]` | Au plus 30, nettoyés et dédupliqués ; 60 caractères maximum par tag. |
| `scope` | `global`, `type`, `project` ; défaut `global` | Règle de visibilité contrôlée par la connexion. |
| `scope_id` | `str`, `""` | Identifiant d’un groupe existant obligatoire pour un type ou projet ; vidé en global. |
| `status` | `published`, `draft`, `archived` ; défaut `published` | Les lectures MCP exposent uniquement les fiches publiées. |

## Champs d’un Skill {#skill}

`Method` ajoute `content`, obligatoire et non vide (100 000 caractères maximum), et `summary`, facultatif (vide par défaut, 600 caractères maximum). Les fiches retournées ajoutent `id`, `version`, `created_at` et `updated_at`. Une recherche retourne `{items, total}` ; ses éléments Skill contiennent les résumés, pas le contenu intégral. Lisez l’identifiant choisi pour récupérer son contenu.

```json
{"title":"Relire une version","content":"Examiner les fichiers sortants avant publication.","category":"Publication","tags":["github"],"scope":"global","status":"published"}
```

## Champs d’une image {#image}

`ImageDescription` ajoute `description`, obligatoire et non vide (30 000 caractères maximum), `preserve`, `avoid` et `usage` (vides par défaut, 15 000 chacun maximum), et `source` (vide par défaut, 2 000 maximum). Les fiches retournées ajoutent identifiant, version, dates et métadonnées de l’original : dimensions, format, SHA-256. `get_image` ajoute `original_path` ; `view_image` retourne des blocs de contenu MCP texte/image.

L’import exige exactement un argument parmi `file_path` et `data_base64`. Les images fixes PNG, JPEG et WebP sont acceptées : 20 Mio, 8192 pixels par côté et 25 millions de pixels maximum. Une mise à jour modifie les descriptions, jamais les pixels de l’original. Voir les [références d’images](doc:images#content).

## Modifications et erreurs {#updates}

Transmettez l’entier `version` courant dans `expected_version` pour modifier une fiche. Une version dépassée produit un conflit au lieu d’écraser une autre modification. Relisez et conciliez les changements. L’écriture exige aussi une connexion autorisée et une portée accessible ; données invalides, fiches inaccessibles et images non prises en charge échouent sans élargir les droits.
