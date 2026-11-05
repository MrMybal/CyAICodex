# CyDoc vendored build dependency

- Upstream: https://github.com/MrMybal/CyDoc
- Version: 0.1.0
- Git commit: `774f2a7eabf7dd181a98ffc5add115b580b67f42`
- Archive SHA-256: `c7a6acf0e7ff982a937312ac43fda4393fea200094e0563ca10c2221b0b10ea7`
- License: MIT, preserved in LICENSE and in the installed help/CyDoc.LICENSE.txt.

The upstream package is not published on npm. This archive was made from that commit using `npm ci`, `npm run build` and `npm pack --ignore-scripts`; it is unmodified. The application installs the archive through package-lock.json. Build dependencies are pinned there. Three.js is an optional upstream peer and is not installed by this application.

To update, check out the intended upstream commit using authenticated Git, read its AI integration guides, build and pack it, replace the archive, update package.json and this provenance, regenerate the lockfile, and run all documentation checks. Do not vendor credentials, personal libraries, node_modules or the upstream checkout. CyDoc's AGENTS.md inside the archive is upstream project material, not an instruction for the host application.
