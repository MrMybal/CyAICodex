---
id: building-help
title: Générer et maintenir la documentation
description: Sources, compilation, intégration locale et contrats de traduction.
section: Intégration
order: 240
revision: 1
sourceRevision: 1
---

## Générer et maintenir le manuel {#content}

L’application Windows utilise Python (FastAPI, SQLite et pystray), avec une interface dans le navigateur. La documentation est un lecteur CyDoc séparé, livré avec elle. Il s’ouvre par une URL de fichier locale et se lit sans serveur applicatif, Python, Node.js, compte IA ni Internet. Le code source peut aussi fonctionner sur une plateforme équipée de Python et d’un navigateur ; l’exécutable et l’installateur distribués ciblent Windows x64.

## Régénérer et distribuer {#build}

Installez Node.js 22 ou plus récent pour la génération, ainsi que l’environnement Python de compilation de l’application. Depuis la racine du dépôt :

```powershell
npm ci
npm run docs:build
npm run docs:check
.\.venv\Scripts\python.exe -m pytest -q
node tests/help_browser.cjs
node tests/i18n_browser.cjs
.\Build-App.ps1
.\Build-Installer.ps1 -Iscc "chemin vers ISCC.exe"
```

Les deux commandes docs régénèrent l’export et valident liens, médias, alias et traductions. Elles nettoient uniquement build/help et build/cydoc-input, sans supprimer les sources rédigées. Build-App et Build-Installer installent les dépendances Node verrouillées, génèrent la documentation et embarquent tout build/help dans _internal/help. PyInstaller utilise une distribution onedir : ouvrir le lecteur ne crée pas un nouveau dossier temporaire à chaque fois. Utilisez l’installateur pour mettre à jour une installation.

L’export autonome est build/help/index.html. Copiez tout le dossier build/help pour le distribuer séparément : data.js, scripts et styles du lecteur, scripts des modules sélectionnés, ressources, manifestes, rapport de traduction et licence. Copier seulement index.html ne suffit pas.

## Contenu et périmètre {#sources}

Rédigez les guides dans docs/content/en et docs/content/fr. Les captures et le logo inchangé sont dans docs/assets. La génération inclut aussi le README du dépôt dans chaque langue, la licence, les notes de version et les annotations Python d’intégration de l’aide. Le README devient la page Référence de l’application. Ses titres sont rendus en gras pour ne pas dériver les ancres publiques de titres traduits ; son ancre d’entrée stable est content.

La liste explicite des sources extraites contient uniquement skills/documentation.py, via l’API publique extractComments de CyDoc et ses annotations Python @doc dans des chaînes entre triples guillemets. Aucune base personnelle, journal, clé, fichier d’environnement, copie de dépôt ignorée ou index de disque complet n’est importé. La référence existante des outils MCP et les guides de connexion restent des descriptions produites à l’exécution ; télécharger un guide de configuration reste une fonctionnalité MCP conservée. Cette application Python ne prétend pas utiliser Doxygen, TypeDoc, une indexation sémantique C++ ou une génération automatique complète d’API.

## Adresses stables {#addresses}

Conservez les mêmes identifiants de pages, d’ancres et de médias dans les deux langues. Le texte traduit peut évoluer indépendamment. Exemples de liens :

```markdown
[Restaurer une sauvegarde](doc:backup#restore)
[Capture des Skills](doc:skills?media=skills-illustration)
```

Les vingt identifiants de chapitres existants sont conservés. Les alias overview → welcome, quickstart → quick-start et api-links → tools sont déclarés dans cydoc.config.json. Ajoutez un alias avant de renommer une page publiée. Les routes sont index.html#/fr/backup/restore ou index.html#/fr/skills?media=skills-illustration ; l’état du média se place après le fragment.

L’hôte Python utilise Path.as_uri() avant d’ajouter la route encodée. Il valide page, ancre et média contre l’export. Consultez [l’intégration Python](doc:help-integration#contracts).

## Ouvrir l’aide depuis l’application {#entry-points}

Documentation dans la navigation et le menu Windows ouvre l’accueil. Le bouton ? et F1 ciblent l’écran actif : Skills, Images, Projets, Assistant, Connexions MCP ou Fournisseurs/paramètres. Dans les dialogues de skill et d’image, F1 cible le chapitre correspondant. Un contrôle peut préciser data-help-page, data-help-section et data-help-media pour une destination plus fine.

```powershell
CyAICodex.exe --open-help --help-language fr --help-page backup --help-section restore
CyAICodex.exe --open-help --help-page skills --help-media skills-illustration
CyAICodex.exe --open-help --help-page quick-start --print-help-url
```

La dernière commande affiche l’URL validée sans navigateur ni serveur. Avec les sources, remplacez CyAICodex.exe par .\.venv\Scripts\python.exe run.py. Le POST authentifié /api/help/open est un lanceur natif et ne sert pas le lecteur. Un site anonyme ne peut pas l’appeler. Les anciens liens /help?lang=fr#backup conservent leur chapitre via le lanceur si l’application tourne et que la session du navigateur est authentifiée ; sinon utilisez le menu Windows ou l’exécutable. L’ancien JSON /help/content retourne HTTP 410 avec des indications.

## Langues et suivi des traductions {#translations}

L’anglais est la langue par défaut du contenu et le français est fourni intégralement. Les nouvelles ouvertures transmettent la langue enregistrée dans l’application ; le sélecteur propre au lecteur change sa vue sans modifier ce réglage. CyDoc affiche l’anglais lorsqu’une traduction manque et signale ce repli. Les compilations exigent les deux langues pour chaque page, les mêmes ancres et aucune traduction manquante, obsolète ou non suivie.

Augmentez revision dans les métadonnées anglaises quand le sens change. Modifiez sourceRevision en français seulement après révision et mise à jour de la traduction. Pour les pages générées, utilisez revision et sourceRevision.fr dans docs/generated-revisions.json ; les annotations de CyDoc 0.1.0 n’acceptent pas elles-mêmes ces balises de révision. Maintenez le changelog traduit avec les notes anglaises. Ne marquez jamais une modification non traduite comme à jour uniquement pour faire passer la validation. La page générée Rapport de traduction et translation-report.json indiquent l’état.

## Modules et ressources locales {#modules}

Seul image est activé : les captures profitent du zoom, du déplacement et de l’agrandissement dans la fenêtre. Leurs contrôles sont épurés et restent accessibles au focus ou sur écran tactile. Les schémas de flux deviennent des SVG statiques accessibles avec leur description textuelle ; graph n’est pas nécessaire. Le manuel existant ne contient ni vidéo, contrôle d’images GIF, modèle 3D ou collection de médias : video, gif, mesh, gallery et graph sont exclus. Three.js n’est ni installé ni livré.

Utilisez les blocs JSON CyDoc avec des chemins commençant par assets/. N’ajoutez ni script distant, police CDN, image externe ou chargement JSON par le réseau à l’exécution. L’exporteur CyDoc fournit des scripts classiques et des fournisseurs locaux pour les ressources et les modules. L’enveloppe docs/reader.html appartient à l’application et définit son identité ainsi qu’un balisage initial anglais ; assets/host.js distingue sa licence AGPL de celle du lecteur CyDoc MIT sans modifier les bundles CyDoc.

## Apparence, accessibilité et lecture {#experience}

Les thèmes clair et sombre CyDoc ont des accents verts cohérents avec l’application. Le choix de thème, la navigation clavier, la recherche locale, le sommaire, l’impression, l’agrandissement intégré et les contrôles tactiles restent disponibles. Échap quitte l’agrandissement ; zoom et annotations restent dans la fenêtre du lecteur. Les captures ont un texte alternatif descriptif et les schémas leur explication complète.

Les positions de lecture, favoris et notes utilisent l’espace de stockage stable CyAICodex de CyDoc. Une politique du navigateur peut bloquer la persistance des origines file ; le manuel reste lisible et permet d’exporter les données personnelles du lecteur. Les anciennes positions ne sont pas importées : l’ancien manuel ne conservait pas de position par chapitre. Changer de chemin d’installation ou de navigateur peut changer le stockage de l’origine fichier. Vérifiez stockage, clavier et gestes tactiles dans le navigateur distribué.

## Vérification et limites connues {#verification}

Après une modification, lancez docs:check, la suite Python et les deux bancs DOM Node. Ils vérifient les identifiants et ancres bilingues, les ressources locales, les seuls modules autorisés, les requêtes d’aide contextuelle, l’authentification et l’encodage des URL. Testez la commande --print-help-url de l’exécutable pour contrôler le chemin livré indépendamment du serveur.

Dans le navigateur Windows cible, ouvrez directement le fichier hors ligne, puis vérifiez lien interne, ancre, changement de langue, recherche, agrandissement d’une capture/Échap, focus clavier, reprise de lecture et chaque entrée d’aide. Un banc DOM et un export réussi ne prouvent pas le comportement natif du navigateur. Les autres systèmes et appareils tactiles nécessitent leurs propres essais. Aucun codec ou WebGL n’est requis puisqu’aucun module vidéo ou mesh n’est activé.
