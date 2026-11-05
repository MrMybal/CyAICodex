---
id: search
title: Retrouver la bonne ressource
description: La recherche plein texte SQLite normalise les accents, accepte les préfixes et privilégie titres, résumés et tags. Plusieurs mots resserrent les résultats. Ce n’est pas une recherche sémantique ou vectorielle.
section: Guide utilisateur
order: 3
revision: 1
sourceRevision: 1
---

## Retrouver la bonne ressource {#content}


1. Saisissez quelques mots significatifs : fragment de titre, tag ou terme du résumé et du contenu.
2. Combinez avec les filtres de catégorie, contexte et état. Activez Inclure les skills globaux si nécessaire dans un projet.
3. Parcourez avec Précédent et Suivant. Effacez texte et catégorie si une fiche attendue manque.

La recherche plein texte SQLite normalise les accents, accepte les préfixes et privilégie titres, résumés et tags. Plusieurs mots resserrent les résultats. Ce n’est pas une recherche sémantique ou vectorielle.

L’interface peut afficher brouillons et archives via le filtre d’état. MCP ne renvoie que les ressources publiées dans la portée de la connexion, avec des extraits courts ; get_skill récupère la fiche complète.

```callout
{"type": "tip", "title": "À retenir", "body": "Un résultat vide peut venir de la portée, de l’état publié ou des mots saisis. Vérifiez get_context avant de conclure à une déconnexion."}
```
