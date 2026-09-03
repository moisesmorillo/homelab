# Kubernetes

This tree will be reconciled by Flux after the K3s cluster is rebuilt. For now, it contains only
a verifiable Kustomize base and the shared namespace for network services.

```text
clusters/homelab/   cluster entry point
infrastructure/     components required before applications
```

## Local rendering

From the repository root, use the version pinned by the project:

```bash
make kustomize
```

Tailscale was intentionally not copied from the previous repository layout. It will be
reintroduced as a `HelmRelease` with:

- a pinned chart and version;
- the subnet route supplied by the private configuration overlay as `<LAN_CIDR>`;
- OAuth credentials encrypted with SOPS;
- exit-node functionality disabled by default;
- ACLs and tags reviewed before any route is approved.

Flux bootstrap will create `flux-system`. Do not add it manually before the replacement cluster
exists and the Git authentication method has been agreed upon.
