# Architecture

## Principles

1. Basic network services must not depend on the Kubernetes cluster.
2. Every resource has one declarative owner.
3. Git contains configuration and encrypted secrets, never plaintext secrets.
4. Network changes preserve a tested recovery path.
5. Existing resources are adopted before replacement is considered.
6. Environment-specific topology remains in an external private overlay.

## Conceptual topology

This diagram describes roles and dependencies only. It does not represent a discovered or
currently verified environment.

```text
Internet uplink
      |
Edge gateway and DHCP
      |
Core switching
      |-- Primary DNS service
      |-- Secondary DNS service
      |-- Kubernetes control-plane and worker nodes
      |-- Virtualization hosts and guests
      `-- Management endpoints
```

DNS and the default gateway remain outside Kubernetes so cluster maintenance cannot remove
basic household connectivity. A future gateway replacement must be performed as an independent
change window after DNS and recovery paths have been validated.

## Declarative ownership

| Resource | Owner | Must not be managed by |
| --- | --- | --- |
| Virtual machines and containers | OpenTofu | Ansible |
| Guest operating systems | Ansible | OpenTofu |
| Physical-host networking | Ansible | Flux |
| Kubernetes installation and base configuration | Ansible | Flux |
| Objects inside Kubernetes | Flux | Ansible |
| DNS synchronization | DNS platform | Flux |
| Gateway, firewall, DHCP, and VLANs | Edge gateway | DNS platform |

The ownership decision is recorded in
[`adr/0001-automation-boundaries.md`](adr/0001-automation-boundaries.md).

## Public and private configuration

The tracked repository documents schemas, safety controls, and reusable automation. Exact
subnets, addresses, hostnames, inventory, hardware identifiers, physical placement, and observed
state belong in the external private overlay. Public examples use documentation-only address
ranges and must never be applied unchanged.
