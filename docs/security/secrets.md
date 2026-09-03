# Secret management

## Policy

- Never commit credentials, tokens, private keys, administrative kubeconfigs, or OpenTofu state
  in plaintext.
- Kubernetes secrets use SOPS with age after the operator provides a public recipient.
- Ansible receives secrets from SOPS, an external secret manager, or environment variables;
  plaintext secrets do not belong in inventory variables.
- OpenTofu receives provider credentials through environment variables. State is stored outside
  Git or in an encrypted remote backend with restricted access.
- DNS administration uses unique credentials per environment and encrypted backups.
- Exact topology, production inventory, and live-state notes remain in a private overlay outside
  the public repository even when they contain no credentials.

## Before enabling SOPS

1. Create or select an age identity outside the repository.
2. Share only its public recipient (`age1...`).
3. Add `.sops.yaml` with that recipient.
4. Encrypt a test secret and confirm that `sops -d` works locally.
5. Keep CI validation that rejects unencrypted Kubernetes `Secret` manifests.

Until these steps are complete, the tracked repository must contain no secret manifests.
