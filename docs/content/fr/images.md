---
id: images
title: Images et consignes de préservation
description: Les images publiées suivent les mêmes règles de contexte et d’écriture que les Skills. get_image fournit métadonnées et chemin local de l’original pour les clients sur ce PC ; view_image fournit un aperçu. Un chemin local n’est pas un lien de téléchargement cloud.
section: Guide utilisateur
order: 6
revision: 1
sourceRevision: 1
---

## Images et consignes de préservation {#content}


1. Ouvrez Ressources d’images > Importer une image et choisissez un PNG, JPEG ou WebP fixe.
2. Décrivez l’image : éléments à préserver, changements à éviter, usages autorisés et source. Ajoutez catégorie, tags, portée et état.
3. Enregistrez et vérifiez la transparence sur le damier de l’aperçu. Télécharger l’original restitue le fichier importé.
4. Modifiez les consignes sur la ressource existante ; importez une variante visuelle comme nouvelle ressource. Utiliser avec l’assistant sélectionne l’image pour la prochaine demande.

| Limite | Valeur |
| --- | --- |
| Taille | 20 Mio maximum. |
| Dimensions | 8192 pixels par côté et 25 millions de pixels maximum. |
| Aperçu | PNG, jusqu’à 1024 pixels. |
| Original | Conservé sans modification avec empreinte SHA-256, dimensions et format. |

Les images publiées suivent les mêmes règles de contexte et d’écriture que les Skills. get_image fournit métadonnées et chemin local de l’original pour les clients sur ce PC ; view_image fournit un aperçu. Un chemin local n’est pas un lien de téléchargement cloud.

```callout
{"type": "tip", "title": "À retenir", "body": "CyAICodex conserve références et consignes. Il ne génère ni ne retouche les pixels. Ne remplacez pas l’original par une capture de son aperçu."}
```
