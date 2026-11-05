---
id: updates
title: Mises à jour, migration et désinstallation
description: La recherche automatique, si activée, a lieu peu après le lancement puis toutes les six heures. Elle n’installe rien automatiquement. Brouillons, préversions, anciennes versions et fichiers sans empreinte attendue valide ne sont pas installés.
section: Guide utilisateur
order: 15
revision: 1
sourceRevision: 1
---

## Mises à jour, migration et désinstallation {#content}


1. Ouvrez Paramètres > Mises à jour et Vérifier les mises à jour.
2. Pour un dépôt privé, activez les identifiants Git GitHub locaux ou fournissez un jeton limité au dépôt avec Contents en lecture. Les releases publiques ne nécessitent pas d’authentification.
3. Si une version stable plus récente est proposée, Télécharger et installer contrôle taille et empreinte SHA-256 GitHub avant d’ouvrir l’assistant.
4. Terminez l’installation et son écran de licence. Serveur et connexions s’arrêtent temporairement. Rouvrez puis reconnectez les clients.

La recherche automatique, si activée, a lieu peu après le lancement puis toutes les six heures. Elle n’installe rien automatiquement. Brouillons, préversions, anciennes versions et fichiers sans empreinte attendue valide ne sont pas installés.

## Migration du portable {#portable-migration}

Quittez la version portable puis lancez l’installateur avec /LEGACYDATA="chemin absolu du dossier data". Il copie une bibliothèque cohérente et préserve l’original. Une bibliothèque existante à destination n’est pas remplacée. Les entrées MCP reconnues sont adaptées sans retirer les autres serveurs ; utilisez Configurer et tester pour une réparation manuelle.

L’installation se trouve normalement dans %LOCALAPPDATA%\Programs\CyAICodex. Désinstallez via les applications Windows ou le désinstalleur installé. La bibliothèque de %LOCALAPPDATA%\CyAICodex\data est conservée. Cela ne révoque pas les comptes externes et ne supprime pas toutes les configurations des clients IA.
