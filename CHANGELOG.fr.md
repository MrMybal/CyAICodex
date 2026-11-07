# Historique des versions

[English](CHANGELOG.md) · [README](README.fr.md) · [Version 0.9.1](https://github.com/MrMybal/CyAICodex/releases/tag/v0.9.1)

## Version actuelle et statut

**CyAICodex 0.9.1 · Bêta · Windows x64.** Disponible pour les essais et retours avant une disponibilité stable.

### Limites documentées

- Seul un installateur Windows x64 est publié. L’installateur et l’exécutable ne sont pas signés avec Authenticode.
- Le serveur reste local à un PC éveillé. Il n’existe ni synchronisation cloud ni bibliothèque multi-appareils ; un client cloud distant ne peut pas joindre directement le localhost de ce PC.
- La recherche est lexicale, sans embeddings ni similarité sémantique.
- Les références d’images sont des PNG, JPEG ou WebP fixes ; CyAICodex conserve originaux et consignes, sans générer d’images. La vision dépend du fournisseur et du modèle.
- L’assistant intégré ne propose ni reprise de session native d’un fournisseur ni affichage token par token. Enregistrez le travail utile dans des Skills ou documents.
- L’export JSON couvre les Skills et leur classement, pas une sauvegarde complète, et il n’y a pas de bouton général d’import JSON. Une sauvegarde complète copie tout le dossier de données après arrêt de l’application.

### Signalements de problèmes

Ces notes ne publient pas de liste séparée détaillant chaque bug. Utilisez le [suivi des problèmes](https://github.com/MrMybal/CyAICodex/issues) pour les signalements actuels et le [guide de dépannage](https://mrmybal.github.io/CyAICodex/Documentation.html#/fr/troubleshooting) pour le diagnostic. Lors d’un signalement, indiquez la version et des étapes de reproduction expurgées des données privées.

## 0.9.1

- Mise à jour du lecteur CyDoc embarqué : recherche dans l’en-tête, Ctrl+K, arborescence, descriptions des titres, thèmes et reprise de lecture.
- Guides utilisateur et références publiques MCP/Python complets en anglais et en français, avec captures et schémas localisés.
- Consignes pour les IA séparées dans DocAI.md ; fichiers de génération exclus du manuel installé.
- Installation de Documentation/Documentation.html à côté de l’exécutable et conservation des liens de chapitres et des accès à l’aide.

## 0.9.0

- Migration de toute la documentation anglaise et française vers le lecteur local CyDoc embarqué.
- Ouverture de l’aide depuis Documentation, l’aide contextuelle, F1, l’icône Windows ou --open-help, sans serveur documentaire.
- Conservation des identifiants de chapitres et des anciens liens compatibles ; zoom et agrandissement des images dans la fenêtre.
- Génération et validation de la documentation dans le build de l’application, avec révisions explicites des traductions.

## 0.8.0

- Ajout d’une rubrique Documentation complète hors connexion, en anglais et en français, avec l’anglais par défaut.
- Vingt chapitres consultables par recherche couvrent les Skills, images, projets, connexions MCP, fournisseurs, droits, sauvegardes, mises à jour et dépannage.
- Captures bilingues et schémas accessibles embarqués ; ouverture séparée du manuel et impression du chapitre choisi.
- Licence AGPL v3 incluse dans l’installateur et l’application installée.

## 0.7.1

- Aide de connexion adaptée à chaque client avec l’outil MCP en lecture seule get_setup_guide.
- Téléchargement d’un guide Markdown anglais ou français depuis Connexions pour le partager avec une IA avant sa connexion.
- Liens de découverte du guide dans /mcp-info, avec étapes de vérification et de dépannage.

## 0.7.0

- Renommage des méthodes de la bibliothèque en Skills et adoption de noms anglais pour les dossiers source et scripts.
- Exemple de Skill de confidentialité GitHub dans les deux langues. Les adaptations existantes sont conservées ; seule la langue manquante est ajoutée.
- Outils MCP search_skills, get_skill, create_skill et update_skill, avec maintien des anciens noms pour les clients existants.
- Notes de version regroupées dans cet historique. L’anglais reste la langue d’interface par défaut ; le français est disponible.

## 0.6.3

- Anglais par défaut en préservant les préférences de langue enregistrées.
- Présentation du dépôt en anglais et documentation française séparée.

## 0.6.2

- Composants partagés installés une seule fois au lieu d’une extraction dans Temp à chaque lancement.

## 0.6.1

- Exemple de checklist avant publication GitHub.

## 0.6.0

- Installateur Windows, transport MCP intégré et mises à jour depuis les releases GitHub.

## 0.5.0

- Connecteurs Antigravity, Command Code, CodeBuddy, OpenRouter et LM Studio.
- Bibliothèque locale existante, portées par projet, références d’images, assistant, icône Windows et interface bilingue.

Les anciennes notes restent dans l’historique Git.
