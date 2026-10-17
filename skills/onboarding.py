"""Public onboarding instructions: no credentials, user paths or library content."""
from typing import Literal
from . import __version__

Client = Literal['all', 'codex', 'claude_desktop', 'claude_code', 'opencode', 'other']
Language = Literal['en', 'fr']
NAMES = {'codex': 'Codex', 'claude_desktop': 'Claude Desktop', 'claude_code': 'Claude Code', 'opencode': 'OpenCode', 'other': 'Other MCP client / Autre client MCP'}


def setup_guide(client: Client = 'all', language: Language = 'en', port: int = 8765):
    if client not in ('all', *NAMES) or language not in ('en', 'fr'):
        raise ValueError('Unsupported client or language')
    french = language == 'fr'
    url = f'http://127.0.0.1:{port}'
    if french:
        intro = '''# Connecter une IA à CyAICodex

Ce guide permet à une IA d’expliquer la configuration à l’utilisateur. Demandez quel logiciel il utilise si nécessaire : Claude Desktop et Claude Code sont deux clients distincts. Adaptez les étapes à sa langue et à son client. Un plugin supplémentaire n’est pas nécessaire pour les clients MCP pris en charge.

## Préparer l’application

1. Installer CyAICodex depuis la release GitHub, puis le démarrer sur le PC Windows.
2. Ouvrir l’interface depuis l’icône de notification Windows.
3. Dans Connexions, choisir le projet ou type de projet, l’accès aux skills globaux et les droits d’écriture souhaités. Respecter le choix de l’utilisateur ; ne pas désactiver les autorisations pour résoudre un problème.
'''
        automatic = 'Ouvrir **Connexions > Configurer et tester**, sélectionner les droits et le contexte souhaités, puis cliquer sur **Configurer et tester** dans la carte de ce client. Reconnecter le serveur MCP dans le client, ou redémarrer le client pour recharger sa configuration.'
        manual = 'Créer une connexion nommée dans **Connexions**, choisir sa portée et ses droits, puis utiliser la configuration générée dans les paramètres MCP du client. Le jeton n’est affiché qu’une fois : le conserver uniquement dans la configuration locale prévue. Suivre le format pris en charge par ce client ; ne pas inventer une commande ou un emplacement de configuration. Reconnecter ensuite son serveur MCP.'
        ending = '''## Vérifier la connexion

- Utiliser **Tester seulement** pour les clients configurés automatiquement. Distinguer « serveur lancé », « client configuré » et « connexion MCP testée ».
- Dans le client IA, vérifier que les outils CyAICodex sont disponibles, appeler `get_context`, puis `search_skills` et `get_skill` si une fiche est trouvée.
- Une liste vide peut simplement correspondre au contexte choisi ou à l’absence de fiches publiées. Ce n’est pas forcément une panne.
- Ne pas annoncer une connexion réussie sans résultat de test réel. En cas d’échec, demander le message d’erreur sans jeton, vérifier que l’application tourne, puis reconnecter le serveur. Un jeton absent ou révoqué se répare depuis Connexions.

## Instruction à ajouter au client IA

> Au début de chaque tâche, appelle get_context, puis search_skills et get_skill pour les pratiques pertinentes. Respecte le projet et les droits de cette connexion. Crée ou modifie un skill seulement à ma demande ; utilise expected_version pour les modifications.

## Limites et confidentialité

- Le fichier Markdown explique la procédure ; il n’installe ni ne configure rien tout seul.
- Le transport stdio utilise le même CyAICodex.exe avec --mcp-stdio et peut démarrer le serveur à la demande. Le transport HTTP nécessite que le serveur soit déjà lancé.
- Le localhost de ce PC n’est pas accessible directement depuis une IA hébergée dans le cloud. Ne pas recommander d’exposer le serveur sur Internet pour contourner cette limite.
- Ne jamais demander à l’utilisateur de coller un jeton, une clé API ou une configuration contenant des secrets dans le chat.
- Les anciens noms search_methods/get_method restent compatibles. Les fiches Skills de la bibliothèque ne sont pas automatiquement des paquets SKILL.md installés dans le client.
'''
    else:
        intro = '''# Connect an AI client to CyAICodex

This guide lets an AI explain setup to the user. Ask which application they use when needed: Claude Desktop and Claude Code are distinct clients. Adapt the steps to their language and client. Supported MCP clients do not require an additional plugin.

## Prepare the application

1. Install CyAICodex from its GitHub release, then start it on the Windows PC.
2. Open the interface from the Windows notification-area icon.
3. In Connections, choose the project or project type, global skill access and desired write permissions. Respect the user's choices; do not disable permissions as a troubleshooting shortcut.
'''
        automatic = 'Open **Connections > Configure and test**, select the desired scope and permissions, then click **Configure and test** on this client’s card. Reconnect its MCP server, or restart the client to reload its configuration.'
        manual = 'Create a named connection in **Connections**, choose its scope and permissions, and use the generated configuration in the client’s MCP settings. The token is displayed only once: keep it only in the intended local configuration. Follow the format supported by that client; do not invent a command or configuration path. Reconnect the MCP server afterwards.'
        ending = '''## Verify the connection

- Use **Test only** for automatically configured clients. Distinguish server running, client configured and MCP connection tested.
- In the AI client, check that CyAICodex tools are available, call `get_context`, then `search_skills` and `get_skill` if a result is found.
- An empty list can reflect the chosen scope or the absence of published records; it does not necessarily indicate a connection failure.
- Never claim success without an actual test result. On failure, ask for the error without credentials, check that the application is running, and reconnect the server. Repair missing or revoked tokens from Connections.

## Instruction to add to the AI client

> At the start of each task, call get_context, then search_skills and get_skill for applicable practices. Respect this connection's project scope and permissions. Create or change a skill only when I ask; use expected_version for updates.

## Limits and privacy

- This Markdown file explains setup; it does not install or configure anything by itself.
- Stdio uses the same CyAICodex.exe with --mcp-stdio and can start the server on demand. HTTP requires the server to be running already.
- A cloud-hosted AI cannot directly reach this PC's localhost. Do not recommend exposing the server to the Internet as a workaround.
- Never ask the user to paste a token, API key or secret-bearing configuration into chat.
- The previous search_methods/get_method names remain compatible. Library Skills are not automatically installed SKILL.md packages in the client.
'''
    selected = list(NAMES) if client == 'all' else [client]
    sections = [f'## {NAMES[key]}\n\n{automatic if key in ("codex", "claude_desktop", "opencode") else manual}\n' for key in selected]
    markdown = intro + '\n' + '\n'.join(sections) + '\n' + ending
    markdown += f'\nCyAICodex {__version__}\n\nMCP: {url}/mcp\n\nDiscovery: {url}/mcp-info\n\nRelease: https://github.com/MrMybal/CyAICodex/releases/latest\n'
    return {'name': 'CyAICodex', 'version': __version__, 'client': client, 'language': language,
            'clients': selected, 'mcp_url': url + '/mcp', 'guide_url': url + f'/mcp-guide?client={client}&lang={language}',
            'markdown': markdown}
