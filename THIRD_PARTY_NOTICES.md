# Third-party software notice

This inactive historical repository references third-party software. Each
component remains governed by its own upstream licence; the repository's
rights reservation does not replace or narrow those licences.

The manifests are not a verified software bill of materials. They contain
version ranges and an unpinned KivyMD development branch. Before running,
building, or distributing any revival, resolve an exact dependency graph,
collect the corresponding licence and NOTICE texts, scan transitive packages,
and review binary-distribution obligations.

Directly referenced families include Kivy/KivyMD, XRPL Py, httpx, websockets,
cryptography, mnemonic, ECPy, requests, IPFS HTTP Client, BigchainDB Driver,
Plyer, Pillow, pytest, Black, flake8, and aiohttp. Their names and marks belong
to their respective owners; mention here identifies compatibility only and
does not imply sponsorship.

Particular review flags:

- `kivymd` points to a moving Git `master` branch rather than a reviewed release.
- the IPFS and BigchainDB version constraints may not resolve to stable releases.
- Android or other binary distribution must reproduce all applicable licence
  and NOTICE material and review copyleft/dynamic-linking obligations.
- no dependency is evidence that the project's broader product concept is
  novel, exclusive, endorsed, or patent-clear.

This file is a compliance checkpoint, not a conclusion that every historical
artifact was lawfully distributed.
