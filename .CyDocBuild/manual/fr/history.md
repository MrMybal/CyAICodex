---
id: history
title: Historique et modifications simultanées
description: Consulter les révisions et résoudre un conflit de modifications.
section: Bibliothèque
order: 4
revision: 2
sourceRevision: 2
parent: skills
---


## Consulter une révision enregistrée {#content}


1. Ouvrez un Skill existant puis Historique des versions.
2. Choisissez Reprendre cette version pour charger une ancienne fiche. Relisez avant d’enregistrer.
3. Enregistrez pour créer une nouvelle version courante. Charger une ancienne fiche n’efface pas l’historique ultérieur.

Chaque modification enregistrée crée une révision. Si un autre client a modifié la fiche depuis son ouverture, l’enregistrement signale un conflit au lieu d’écraser sa modification. Rechargez, comparez vos changements et enregistrez volontairement.

Les écritures MCP transmettent expected_version issu de get_skill ou get_image. Un conflit nécessite une nouvelle lecture. L’historique des descriptions ne restaure pas d’anciens pixels : importez les variantes comme ressources distinctes.
