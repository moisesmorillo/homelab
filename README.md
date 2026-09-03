# Homelab

A public-safe GitOps foundation for managing a small homelab with OpenTofu, Ansible, Flux,
Kubernetes, and dedicated DNS.

This repository contains reusable automation, policy, examples, and architecture decisions. It
intentionally does **not** contain the live network map, production inventory, login names,
device identifiers, current-state observations, or credentials.

## Public topology

The useful architectural shape can remain public without publishing operational endpoints:

```text
Internet
   │
Edge gateway / firewall / DHCP
   │
Core switch
   ├── Redundant DNS
   ├── Kubernetes nodes
   ├── Virtualization host
   └── Access network and clients
```

Private addresses are not reachable from the Internet by themselves. The risk comes from
combining addresses with host roles, usernames, management ports, hardware, VPN state, and
recovery details: that map can shorten an attacker's reconnaissance after any foothold. The
public diagram therefore shows trust boundaries and dependencies, not the deployed layout.

See [Architecture](docs/architecture.md) for the ownership model and a larger abstract diagram.

## Public/private boundary

| Location | Purpose | May contain live values? |
| --- | --- | --- |
| This repository | Roles, playbooks, policy, CI, examples, generic runbooks | No |
| Private sibling overlay | Inventory, IPAM, hostnames, environment ID, current state | Yes |
| Secret manager or encrypted store | Passwords, tokens, private keys, kubeconfigs | Yes |

The recommended local layout is:

```text
workspace/
├── homelab/          # this public repository
└── homelab-local/    # private operational overlay; never publish
```

The example files use IETF documentation addresses and `.invalid` hostnames. An empty CI
inventory is the default. Live playbooks require an explicit overlay, target, environment
confirmation, and apply flag; the role repeats those checks before any mutation.

The complete policy is documented in [Public repository boundary](docs/security/public-repo.md).

## Ownership boundaries

| Layer | Owner | Responsibility |
| --- | --- | --- |
| Virtual infrastructure | OpenTofu | VM/container lifecycle and virtual hardware |
| Linux hosts | Ansible | Operating system, host networking, packages, DNS, K3s bootstrap |
| Kubernetes objects | Flux | In-cluster infrastructure and applications |
| DNS data | DNS platform | Resolution, filtering, replication, and backups |
| Gateway and DHCP | Edge firewall | Routing, firewall policy, leases, and VLANs |

See [ADR 0001](docs/adr/0001-automation-boundaries.md) for the rationale.

## Repository layout

```text
ansible/      reusable host automation and non-routable example inventory
config/       documentation-only example data
docs/         public architecture, policy, decisions, and parameterized runbooks
kubernetes/   minimal Kustomize base for later Flux reconciliation
tofu/         safe adoption guidance; resources follow live inspection
tools/        validation and public-boundary checks
```

## Validation

Python 3.12+ and Go 1.23+ are required.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
make validate
```

Validation covers YAML, Ansible syntax and linting, Kustomize rendering, plaintext Kubernetes
Secrets, and mechanically detectable boundary violations. Semantic review is still required to
ensure that examples do not reproduce live names, identifiers, placements, or role mappings.

## Operating against a private overlay

First validate the sibling overlay without contacting a host:

```bash
make overlay-check \
  OVERLAY_DIR=../homelab-local \
  TARGET_HOST=sample-node-a \
  CONFIRM=your-private-environment-id
```

Then preview one explicitly named host. `CONFIRM` must exactly match the private overlay's
environment ID:

```bash
make network-plan \
  OVERLAY_DIR=../homelab-local \
  TARGET_HOST=sample-node-a \
  CONFIRM=your-private-environment-id
```

Do not run `make network-apply` until the preview and the
[edge-node migration runbook](docs/runbooks/edge-node-network-migration.md) have both been
reviewed from a recovery-capable console.

## Security principles

- Assume attackers know the public architecture and software choices.
- Expose no administration interface directly to the Internet.
- Keep live inventory and state outside this Git history.
- Store no plaintext credentials, private keys, administrative kubeconfigs, or state files.
- Pin versions and verify backups before destructive adoption or rebuild operations.
- Keep DNS and gateway services independent from the Kubernetes cluster.
