# Skill Agent CyAICodex

[English](README.md) · [SKILL.md](cyaicodex/SKILL.md)

Un même `cyaicodex/SKILL.md` portable pour Codex, Claude Code et les clients compatibles Agent Skills. Il indique à l’agent comment consulter la bibliothèque, lire les pratiques utiles, respecter les portées par projet et utiliser les références, sans enregistrer de fiche sans demande. Les consignes sont en anglais ; l’agent répond dans la langue de l’utilisateur. Aucun paramètre propre à un fournisseur, compte ou identifiant MCP n’est embarqué.

## Installer dans Codex et Claude Code

Depuis une copie des sources, avec PowerShell 7 :

```powershell
pwsh -File .\integrations\skills\Install-Skill.ps1 -Client all
```

Pour une installation manuelle, copiez le dossier `cyaicodex` complet dans un des emplacements ci-dessous. Cela fonctionne aussi si l’exécution des scripts est restreinte, sans changer la politique d’exécution.

Choisissez `-Client codex` ou `-Client claude-code` pour un seul client. `-WhatIf` affiche les changements prévus. Les fichiers identiques restent intacts ; les fichiers différents demandent `-Update`, qui conserve une sauvegarde `.previous` de chaque fichier du paquet remplacé et préserve les autres fichiers. L’installation dans votre profil ne demande pas de droits administrateur.

| Client | Installation utilisateur | Installation par projet |
| --- | --- | --- |
| Codex | `~/.agents/skills/cyaicodex/` | `.agents/skills/cyaicodex/` |
| Claude Code | `~/.claude/skills/cyaicodex/` | `.claude/skills/cyaicodex/` |

Utilisez `-Scope Project -RootPath "chemin du projet"` pour un projet précis. Avec la portée utilisateur par défaut, `-RootPath` choisit un autre dossier de profil. Si une version ancienne ou personnalisée de Codex lit plutôt `~/.codex/skills`, copiez-y manuellement le même dossier `cyaicodex` ; évitez les doublons entre plusieurs emplacements lus par le même client. Les autres clients peuvent utiliser leur dossier Agent Skills documenté.

Le Skill devient disponible après actualisation des Skills par le client : prochain tour ou nouvelle session selon sa version. Appelez `$cyaicodex` dans Codex ou `/cyaicodex` dans Claude Code, par exemple : « Cherche dans CyAICodex la checklist de publication applicable. » Les métadonnées permettent la sélection automatique, sans garantir une consultation à chaque tour. Ajoutez une consigne permanente dans le client si vous exigez cette consultation au début de chaque tâche.

## Application Claude / claude.ai

Téléchargez [CyAICodex-Skill.zip](https://mrmybal.github.io/CyAICodex/AgentSkills/CyAICodex-Skill.zip), puis importez-le et activez-le dans **Personnaliser > Skills**, si votre offre et votre espace autorisent les Skills personnalisés. Le ZIP contient un seul dossier `cyaicodex/`, avec `SKILL.md` et sa licence. Le [SKILL.md seul est aussi consultable](https://mrmybal.github.io/CyAICodex/AgentSkills/SKILL.md). Importer le ZIP ne demande aucune exécution de script.

Les environnements desktop, Code et cloud ne partagent pas tous les mêmes fichiers locaux ni les mêmes outils. Importer le Skill ne rend pas le serveur MCP local accessible depuis une session cloud.

## Connecter MCP séparément

Démarrez CyAICodex. Pour Codex ou Claude Desktop, ouvrez **Connexions > Configurer et tester**, choisissez contexte et droits, puis reconnectez le serveur MCP dans le client. Claude Code utilise la configuration générée dans ses paramètres MCP. Demandez à l’agent d’appeler `get_context`, puis `search_skills` et `get_skill` pour une fiche pertinente. Ne collez pas de jeton dans le chat.

Le Skill installe seulement des consignes. Il n’installe pas CyAICodex, ne configure pas de serveur, ne change pas les droits et ne copie pas votre bibliothèque dans le client. Une session cloud ne peut pas joindre directement le localhost de votre PC. Consultez le [vrai manuel de connexion](https://mrmybal.github.io/CyAICodex/Documentation.html#/fr/mcp).

## Générer le téléchargement

```powershell
python tools/package_agent_skill.py
```

La commande crée `dist/agent-skills/CyAICodex-Skill.zip`, `SKILL.md` et `SHA256SUMS.txt`, sans Git, réseau ni dépendance Python tierce. La génération documentaire ajoute les mêmes fichiers dans `Documentation/AgentSkills/` ; la prochaine compilation de l’application les embarquera avec son manuel. `node website/build-pages.mjs` les publie dans `AgentSkills/`. Les sources restent ici ; les archives générées restent hors de Git. L’installateur actuel de l’application n’acquiert pas automatiquement ce nouveau Skill.

Références du format : [Skills Codex](https://learn.chatgpt.com/docs/build-skills), [Skills Claude Code](https://code.claude.com/docs/en/skills), [import ZIP dans Claude](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills). Le paquet conserve la licence AGPL-3.0-only de CyAICodex.
