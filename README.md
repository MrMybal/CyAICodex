# CyAICodex

Maintenance : **Cyberalien**.

Application locale pour Windows : une bibliothèque de pratiques réutilisables, consultable et modifiable par des clients IA via MCP. Interface française et anglaise dans le navigateur et processus persistant dans la zone de notification.

Une méthode d’exemple **Confidentialité avant publication GitHub** est fournie avec l’application : contrôle des sources, historique Git, secrets, données personnelles et fichiers de release. Elle est ajoutée une seule fois, en portée globale et à l’état publié, dans la langue initiale de la bibliothèque (français ou anglais). Elle peut être adaptée ou archivée ; les mises à jour ne remplacent pas les adaptations. Les bibliothèques personnelles sont stockées séparément des exemples distribués.

## Démarrer

Version Windows 0.6.2 : télécharger **CyAICodex-Setup-0.6.2.exe** depuis les releases GitHub, puis suivre l’installation. Ouvrir ensuite **CyAICodex** depuis le menu Démarrer ou son raccourci. Python n’est pas nécessaire pour cette version. Le logo vert « CY » avec un livre apparaît dans la zone de notification et ouvre l’interface locale. `Demarrer.vbs` utilise aussi l’exécutable lorsqu’il est présent.

Pour utiliser les sources, installer Python 3.11 ou plus récent, puis exécuter `Installer.ps1` dans PowerShell. Il crée un environnement Python isolé et installe les versions figées dans `requirements.lock.txt`. `Construire-Exe.ps1` génère l’exécutable autonome dans `dist/CyAICodex/CyAICodex.exe`, avec ses composants dans `_internal`. Conserver ce dossier à côté de l’exécutable : il évite une extraction dans Temp à chaque lancement. Utiliser l’installateur pour les mises à jour. Avec Inno Setup 6, `Construire-Installateur.ps1 -Iscc "chemin vers ISCC.exe"` produit l’installateur. Voir aussi `Lisez-moi-v0.6.2.txt`.

Fermer l’onglet ne coupe pas le serveur. Le menu de l’icône permet de rouvrir l’application, d’activer **Démarrer avec Windows**, ou de quitter et arrêter le serveur. Le démarrage automatique se règle aussi dans **Connexions → Disponibilité du serveur**. Le réglage est partagé avec le menu de l’icône Windows. Il lance le serveur sans ouvrir le navigateur à l’ouverture de la session utilisateur (pas avant la connexion Windows). La version installée conserve les données dans `%LOCALAPPDATA%\CyAICodex\data`, indépendamment des fichiers de l’application. La version portable utilise `data/` à côté de son exécutable. La désinstallation conserve la bibliothèque.

L’interface s’ouvre avec un lien de session depuis l’icône. L’adresse seule peut demander de la rouvrir depuis l’icône. Le jeton de lancement est échangé contre un cookie HttpOnly SameSite=Strict et immédiatement retiré de la barre d’adresse.

## Bibliothèque et contextes

- Fiches avec titre, résumé, contenu Markdown, catégorie et tags.
- États : publiée, brouillon, archivée. Seules les fiches publiées sont consultables par MCP.
- Portées : globale, type de projet, projet précis.
- Recherche SQLite FTS5 : accents normalisés, préfixes, combinaison des mots saisis et classement BM25 privilégiant titre, résumé et tags. Pagination et réponses MCP courtes ; le contenu complet est récupéré à la demande.
- Historique conservé à chaque modification. « Reprendre cette version » charge une ancienne version dans l’éditeur ; enregistrer crée une nouvelle version.
- Contrôle de version optimiste : une modification concurrente renvoie un conflit au lieu d’écraser le travail précédent.
- Export JSON des méthodes et du classement, sans clés ni jetons. Pour une sauvegarde complète avec historique, arrêter l’application puis copier `data/`. Les clés chiffrées restent liées au compte Windows qui les a créées.

Exemple : une connexion pour « Site vitrine », de type « Web », voit les méthodes de ce projet, les méthodes « Web », et les globales si la case correspondante est cochée. Elle ne voit pas les méthodes d’un autre projet. Une connexion limitée à un type voit ce type et éventuellement les globales. Sans projet/type, elle voit uniquement les globales.

Le contexte est attaché au jeton, jamais à un réglage global partagé entre les IA. Créer plusieurs connexions permet donc plusieurs contextes simultanés. Les permissions d’écriture couvrent toutes les méthodes accessibles à cette connexion, y compris les globales si activées.

## Connecter les IA au serveur MCP

Dans **Connexions**, créer une connexion nommée, choisir son contexte et les droits d’écriture. Copier immédiatement la configuration générée : le jeton n’est affiché qu’une fois et seul son condensat SHA-256 est conservé. Révoquer la connexion invalide le jeton.

Transport : **Streamable HTTP**, endpoint par défaut `http://127.0.0.1:8765/mcp`, authentification `Authorization: Bearer <jeton>`. Le serveur utilise le SDK MCP officiel Python, en mode stateless, avec réponses JSON. Plusieurs clients peuvent l’utiliser simultanément.

Outils : `get_context`, `search_methods`, `get_method`, `create_method`, `update_method`. Une ressource `methodes://context` et le prompt `appliquer_methodes` sont également proposés. Les outils déclarent leurs annotations de lecture/écriture.

Dans **Connexions → Configurer et tester**, Codex, Claude Desktop et OpenCode utilisent le même **CyAICodex.exe** avec `--mcp-stdio`. Ce transport intégré démarre le serveur à la demande et partage la bibliothèque entre les clients. Aucune passerelle séparée n’est nécessaire. Les clients HTTP restent compatibles avec le serveur déjà lancé. Les formats génériques ne remplacent pas la configuration propre à chaque client.

Instruction conseillée dans les règles du client IA :

> Au début de chaque tâche, consulte le serveur CyAICodex : get_context, puis search_methods et get_method pour les pratiques applicables. Respecte le contexte de cette connexion. Si une pratique devient réutilisable, enregistre-la quand je te le demande.

MCP donne accès aux pratiques, mais ne peut pas forcer un modèle à les consulter. Les règles de chaque client rendent cette consultation systématique. Une configuration par projet du client permet de sélectionner le jeton correspondant.

## Assistant intégré

### Ressources d’images

L’onglet **Ressources d’images** permet d’importer des PNG, JPEG et WebP fixes (20 Mo maximum, 8192 pixels par côté, 25 mégapixels). Chaque fiche contient une description détaillée, les éléments à préserver, les changements à éviter, les usages autorisés, la source, la catégorie, les tags et la portée globale/type/projet. Les états brouillon, publié et archivé fonctionnent comme pour les méthodes.

Les fichiers originaux sont conservés sans modification dans `data/images/`, avec leur empreinte SHA-256 et leurs dimensions. Les aperçus sont limités à 1024 pixels et affichent la transparence sur un damier de présentation. « Télécharger l’original » restitue le fichier importé. Modifier les consignes conserve leur historique ; une nouvelle variante visuelle s’importe comme une nouvelle ressource.

Les outils MCP `search_images`, `get_image`, `view_image`, `import_image` et `update_image` permettent aux IA de chercher les références, lire les descriptions, voir les aperçus et actualiser les consignes avec contrôle de version. Les mêmes restrictions de projet et de lecture/écriture s’appliquent. `get_image` fournit aussi le chemin local du fichier original pour les clients sur ce PC. Les brouillons et archives ne sont pas exposés au MCP.

« Utiliser avec l’assistant » sélectionne une image et ses consignes pour la prochaine demande. OpenAI et Claude reçoivent un aperçu PNG ; Codex reçoit le fichier original via son option `--image`. Le modèle choisi doit accepter les images. Le sélecteur affiche les 100 ressources les plus récentes, et une ressource plus ancienne peut être sélectionnée depuis sa fiche. L’assistant peut analyser l’image et rédiger des consignes ; cette version n’intègre pas de génération d’images.

Pour sauvegarder la bibliothèque visuelle et l’historique, copier le dossier `data/` complet après avoir arrêté l’application. L’export JSON de la bibliothèque de méthodes n’inclut pas les images.

Références des formats d’entrée : [OpenAI — images et vision](https://developers.openai.com/api/docs/guides/images-vision), [Claude — vision](https://platform.claude.com/docs/en/build-with-claude/vision).

### Fournisseurs

- **Codex / compte ChatGPT** : nécessite le client Codex local accessible dans `PATH`. « Vérifier » lit l’état du compte via le protocole officiel `codex app-server`. « Se connecter » propose son URL d’authentification dans le navigateur. Une connexion existante est réutilisée. Les réponses utilisent `codex exec` en lecture seule, dans un dossier temporaire, sans charger la configuration MCP utilisateur et avec session éphémère.
- **OpenAI API** : clé API et identifiant de modèle ; requêtes à l’API Responses avec `store: false`.
- **Claude API** : clé Anthropic et identifiant de modèle ; requêtes à l’API Messages. L’abonnement Claude grand public n’est pas une clé API.

Les clés locales sont chiffrées par Windows DPAPI, et ne sont jamais renvoyées au navigateur. Les variables `OPENAI_API_KEY` et `ANTHROPIC_API_KEY` sont aussi reconnues au lancement. La requête envoie le texte de la conversation et la méthode de référence choisie au fournisseur. Aucun appel IA n’est nécessaire pour lire, rechercher ou modifier manuellement la bibliothèque.

« En faire une méthode » ouvre un brouillon dans l’éditeur. L’assistant propose le texte ; l’enregistrement reste explicite. La conversation intégrée reste en mémoire dans l’onglet et disparaît au rechargement. Le sélecteur de référence présente les 100 méthodes publiées les plus récentes.

## Portée de cette première version

Le serveur reste accessible uniquement depuis ce PC, lié à `127.0.0.1` avec contrôle Host/Origin. Ce n’est pas un service cloud : ChatGPT web ou un autre service distant ne peuvent pas joindre directement cette adresse. Un relais distant avec authentification demanderait une intégration supplémentaire. Le serveur s’arrête si Windows est éteint ou en veille.

Cette version fournit une recherche lexicale locale, sans embeddings, recherche sémantique ni synchronisation multi-appareils. L’interface s’ouvre dans le navigateur ; l’installateur et l’exécutable ne sont pas encore signés avec un certificat Authenticode. Les méthodes sont stockées en clair dans SQLite pour permettre leur récupération ; protéger l’accès au compte et au disque Windows reste pertinent.

Le dossier `data/`, l’environnement Python et les fichiers `.env` sont exclus dans `.gitignore`. Conserver les réglages propres au poste dans ce dossier local.

## Développement et vérification

```powershell
.\.venv\Scripts\python.exe run.py --headless --no-open
.\.venv\Scripts\python.exe -m pytest -q
node --check methodes/web/app.js
```

Options : `--port 8765`, `--data-dir <dossier>`, `--no-open`, `--headless`.

Les tests couvrent filtrage par contexte, accents et classement, droits en lecture seule, révocation de jeton, concurrence des versions, historique, export sans secrets, authentification locale, protection Host/Origin, chiffrement DPAPI, adaptateurs API avec réponses simulées, et trois clients MCP réels simultanés sur HTTP. Le test DPAPI nécessite un compte Windows normal ; certains environnements sandbox sans profil utilisateur le bloquent.

Fichiers principaux : `methodes/store.py` (SQLite/recherche), `methodes/server.py` (HTTP/MCP), `methodes/assist.py` (fournisseurs), `methodes/desktop.py` (Windows/tray), `methodes/web/` (interface sans dépendances CDN).

Journal local rotatif : `data/methodes.log`.

## Références d’intégration

- [SDK MCP Python officiel](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x)
- [Configuration MCP dans Codex](https://developers.openai.com/codex/mcp/)
- [Authentification via Codex App Server](https://developers.openai.com/codex/app-server/)
- [API OpenAI Responses](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
- [API Claude Messages](https://platform.claude.com/docs/en/api/messages/create)
- [Connexion MCP dans Claude Code](https://code.claude.com/docs/en/mcp)

## Version 0.2 — clients locaux et import MCP

`import_image(description, file_path=..., data_base64=...)` importe une nouvelle référence : fournir exactement un chemin absolu local ou du base64 brut. Les mêmes limites de format/taille, droits d’écriture et restrictions de projet s’appliquent. Le fichier original est conservé. Reconnecter les clients MCP après mise à jour pour actualiser leur liste d’outils.

L’onglet **Paramètres** permet d’activer l’accès MCP sans jeton (désactivé par défaut), de sélectionner son contexte et d’autoriser ou non son écriture. Un jeton invalide reste refusé même si l’accès sans jeton est activé. L’administration reste authentifiée et le serveur reste lié à 127.0.0.1. L’option d’écriture par défaut concerne les nouvelles connexions ; celles déjà créées ont chacune leur case Écriture dans Connexions. Les confirmations propres aux clients IA restent gérées dans ces clients.

La détection de Codex consulte aussi son installation desktop, sans dépendre uniquement du PATH hérité d’Explorer. Des chemins .exe personnalisés sont possibles dans Paramètres.

- **Claude Code / compte Claude** : client local officiel, avec bouton de connexion interactif. Le compte Claude Desktop n’est pas automatiquement une connexion Claude Code. L’assistant utilise le mode print avec images, sans outils et sans persistance de session. Il faut connecter son compte une fois.
- **Claude Desktop / application** : cliquer sur **Configurer et tester** dans Connexions, puis redémarrer Claude. Le même `CyAICodex.exe` assure le transport stdio et démarre le serveur local si nécessaire. Les autres serveurs configurés sont conservés.
- **OpenCode** : client local et ses fournisseurs configurés ; connexion via le bouton dédié. Modèle au format `fournisseur/modèle`. `ollama/qwen3:0.6b` utilise directement l’adresse Ollama définie dans Paramètres. Un format MCP OpenCode est également proposé dans Connexions.
- **Ollama** : serveur HTTP local, aucun secret API requis. Vérifier pour lister les modèles installés, puis utiliser le modèle dans l’assistant. Les petits modèles uniquement textuels ne permettent pas d’analyser les images. Pour les références visuelles, choisir un modèle vision.

`Installer-Clients.ps1` installe les clients officiels Claude Code et OpenCode dans `data/local-clients/` si Node/npm est présent. Ils ne sont pas inclus dans l’exécutable distribué ; les installations natives existantes sont aussi détectées.

Les tests des adaptateurs utilisent des réponses simulées ; les tests réels nécessitent un client installé et un compte ou modèle disponible.

Références : [Claude Code programmatique](https://code.claude.com/docs/en/headless), [options Claude](https://code.claude.com/docs/en/cli-reference), [OpenCode CLI](https://opencode.ai/docs/cli/), [OpenCode et Ollama](https://opencode.ai/docs/providers/#ollama), [Ollama chat](https://docs.ollama.com/api/chat).

## Version 0.3 — connexion guidée et diagnostic MCP

Dans **Connexions → Connecter une IA en un clic**, choisir l’accès puis **Configurer et tester** sur Codex, Claude Desktop ou OpenCode. Le bouton écrit une entrée `cyaicodex` dans la configuration utilisateur officielle, conserve les autres serveurs et sauvegarde le fichier précédent dans `.cyaicodex-backups/` à côté de celui-ci. Les commentaires TOML sont conservés ; les fichiers JSON/JSONC sont réécrits en JSON formaté (l’original et ses commentaires restent dans la sauvegarde). Un fichier invalide ou une entrée du même nom pointant ailleurs n’est pas écrasé.

Le mode sans jeton reprend les droits et le contexte déjà activés dans Paramètres. Le mode avec jeton crée un accès distinct pour chaque client avec le contexte et les droits choisis. Cliquer de nouveau avec les mêmes réglages ne crée pas de doublon. Un jeton révoqué peut être réparé ; seuls les anciens jetons créés par cette configuration automatique sont remplacés. Les connexions manuelles restent conservées.

Le diagnostic sépare **Serveur lancé**, **Client configuré** et **Connexion MCP testée**. Il lit la configuration écrite puis exécute réellement initialize, tools/list et get_context, avec le transport et le jeton configurés. Il ne simule pas une réponse de modèle et ne prouve pas qu’une application déjà ouverte a rechargé ses outils : reconnecter le serveur ou redémarrer le client après configuration. Aucun jeton n’apparaît dans le diagnostic.

Chemins détectés : CODEX_HOME/config.toml (ou ~/.codex/config.toml), Claude Desktop standard ou Microsoft Store, OPENCODE_CONFIG ou XDG_CONFIG_HOME/opencode/opencode.json[c]. Plusieurs profils Claude concurrents sont signalés au lieu de choisir au hasard.

`http://127.0.0.1:8765/mcp-info` expose les informations de connexion sans jeton ni contenu privé. Une simple requête navigateur sur `/mcp` n’est pas un test MCP valide ; utiliser le diagnostic intégré. Le serveur reste local : une IA distante dans un service cloud ne peut pas joindre le localhost de ce PC.

Références : [Codex MCP](https://developers.openai.com/codex/mcp), [Claude Desktop et serveurs locaux](https://modelcontextprotocol.io/docs/develop/connect-local-servers), [OpenCode MCP](https://opencode.ai/docs/mcp-servers/).
## Langues / Languages

CyAICodex propose le français et l’anglais : sélecteur **FR / EN** en haut à droite,
ou **Paramètres > Langue de l’application**. Le choix est conservé localement et
s’applique aussi au menu de notification Windows et à la langue demandée à l’assistant.
Les fiches, projets et ressources ne sont pas traduits automatiquement.

CyAICodex supports French and English. Use the **FR / EN** selector or
**Settings > App language**. The preference is saved locally; user content is unchanged.

Les traductions sont regroupées dans `methodes/web/translations.tsv` (français,
tabulation, anglais). `uiText` traduit un libellé ; `uiHTML` traduit uniquement les
segments statiques des modèles JavaScript, jamais leurs valeurs interpolées.
Les messages de fournisseurs externes non reconnus restent dans leur langue d’origine.
Validation : `python -m pytest -q` et `node tests/i18n_browser.cjs`.

## Version 0.5 — connecteurs supplémentaires

Dans **Paramètres → Connecteurs supplémentaires**, configurez le client ou serveur,
enregistrez, puis utilisez **Vérifier**, **Charger les modèles** ou **Tester une réponse**.
Le test de réponse envoie un message de contrôle au fournisseur choisi ; il peut
consommer son quota. Il ne transmet pas les fiches de la bibliothèque.

| Connecteur | Accès | Transport | Images dans cet adaptateur |
|---|---|---|---|
| Antigravity | Compte du CLI `agy` | stream-json, résultat terminal obligatoire | Non |
| Command Code | CLI `cmdc` / `command-code` | NDJSON, résultat terminal obligatoire | Non |
| CodeBuddy | CLI `codebuddy` / `cbc` | stream-json, outils désactivés | Non |
| OpenRouter | Clé API | HTTPS Chat Completions | Selon le modèle |
| LM Studio | Serveur local démarré dans LM Studio | HTTP Chat Completions sur loopback | Selon le modèle |

Ces cinq connecteurs s’ajoutent à Codex, Claude Code, OpenCode, Ollama, OpenAI API
et Claude API. La connexion de l’application graphique et celle de son CLI peuvent
être distinctes. **Ouvrir le client** permet de terminer sa connexion native.
Command Code et CodeBuddy sont également détectés dans leurs installations npm.

Antigravity et Command Code utilisent le mode plan natif, dans un dossier temporaire ;
leurs règles de lecture et intégrations restent celles du client. Cette application
ne relaie pas leurs demandes d’approbation et n’active pas leurs modes d’exécution sans
confirmation. Pour un assistant sans outils, utiliser CodeBuddy, les adaptateurs
API, Ollama ou LM Studio.

Les réponses sont affichées une fois terminées. L’historique de l’onglet est renvoyé
à chaque demande : cette version ne propose pas de reprise de session native pour
les nouveaux connecteurs. Elle n’affiche pas de progression token par token.
Un modèle manuel reste possible lorsque le catalogue du client n’est pas disponible.
Aucun modèle n’est installé automatiquement par ces boutons.

Les clés sont enregistrées avec Windows DPAPI. Laisser le champ vide conserve la
clé ; **Retirer la clé enregistrée** l’efface. LM Studio accepte uniquement une adresse
HTTP locale finissant par `/v1`. OpenRouter utilise son adresse officielle fixe.
Les métadonnées du dernier test sont locales ; un test réussi ne garantit pas
l’accès ultérieur à tous les modèles.

Le code des transports se trouve dans `methodes/connectors.py`. Il reprend les
conventions de protocole de CyAI Connector Lab sans dépendre d’une installation du Lab.
Les contrats sont testés dans `tests/test_connectors.py` : résultats terminaux,
erreurs, tailles de sortie, délais, résolveur npm et conservation des clés.

Références : [Antigravity](https://antigravity.google/docs/cli/headless/),
[Command Code](https://commandcode.ai/docs/headless),
[CodeBuddy](https://www.codebuddy.ai/docs/cli/cli-reference),
[OpenRouter](https://openrouter.ai/docs/api/reference/overview),
[LM Studio](https://lmstudio.ai/docs/developer/openai-compat/chat-completions).

## Version 0.6 — installation et mises à jour

L’installateur est propre au compte Windows, sans élévation administrateur. Il crée une entrée dans le menu Démarrer, propose un raccourci sur le bureau et le démarrage avec Windows. Le même exécutable gère l’interface, le serveur et le transport MCP stdio. La fermeture d’un client MCP ne ferme pas l’application dans la zone de notification.

Pour migrer depuis une version portable, quitter l’ancienne application et lancer l’installateur avec `/LEGACYDATA="chemin complet du dossier data"`. La bibliothèque est copiée avec une sauvegarde SQLite cohérente ; l’original reste intact. Une bibliothèque déjà présente à destination n’est jamais remplacée. Les configurations MCP reconnues sont adaptées au nouveau chemin en conservant leurs jetons et les autres serveurs. En cas de configuration non reconnue, utiliser **Connexions → Configurer et tester**.

**Paramètres → Mises à jour** vérifie la dernière release stable au démarrage et toutes les six heures (option désactivable). Le bouton **Télécharger et installer** récupère l’installateur, vérifie sa taille et son empreinte SHA-256 GitHub, puis ouvre l’assistant d’installation. L’installation ferme temporairement les connexions MCP ; recharger les clients après la mise à jour. L’installation intégrée concerne Windows et le port standard 8765.

Pour un dépôt privé, activer la connexion GitHub locale de Git ou fournir un jeton limité au dépôt avec **Contents: read**. Le jeton est chiffré par Windows DPAPI et n’est jamais renvoyé par l’API locale. Il n’est transmis qu’à `api.github.com`, jamais aux adresses de redirection des fichiers. Si le dépôt devient public, la vérification et le téléchargement fonctionnent sans compte, même si une ancienne connexion privée est devenue invalide.

Publication d’une mise à jour : créer un tag `vMAJEUR.MINEUR.CORRECTIF` et une release stable contenant `CyAICodex-Setup-MAJEUR.MINEUR.CORRECTIF.exe`. GitHub doit fournir le champ `digest` SHA-256 de cet asset. Les brouillons, préversions, versions plus anciennes et fichiers sans empreinte vérifiable ne sont pas installés.

Références : [MCP Codex](https://developers.openai.com/codex/mcp), [MCP OpenCode](https://opencode.ai/docs/mcp-servers/), [assets des releases GitHub](https://docs.github.com/en/rest/releases/assets), [Inno Setup](https://jrsoftware.org/isinfo.php).
