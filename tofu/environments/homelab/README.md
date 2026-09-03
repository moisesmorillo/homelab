# Homelab environment

This directory is reserved for the Proxmox root module. It intentionally contains no resources
until the existing infrastructure has been inventoried and an adoption plan has been approved.

Production endpoints and resource identifiers must come from the private operator overlay.
Credentials must be supplied through environment variables or an approved secret manager, and
state must never be stored in Git. See [`../../README.md`](../../README.md) for the safe adoption
sequence.
