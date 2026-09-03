# ADR 0001: Automation boundaries

- Status: Accepted
- Date: 2026-09-02

## Context

The homelab combines physical hardware, virtual resources, operating systems, and Kubernetes.
The previous repository mixed installation, deployment, and network changes in one imperative
workflow without a dependable rollback boundary.

## Decision

- OpenTofu owns the lifecycle and virtual hardware of virtual machines and containers.
- Ansible owns Linux hosts, operating-system networking, packages, DNS software, and the
  Kubernetes installation.
- Flux exclusively owns resources inside Kubernetes.
- The DNS platform uses its native synchronization mechanism between resolver instances.
- The active edge gateway retains routing and DHCP until a replacement platform is ready.
- SOPS with age is the format for versioned secrets; encryption uses only a public recipient.
- Exact topology and observed state remain in an external private overlay.

## Consequences

- No resource has two declarative owners.
- A virtual guest is created or adopted with OpenTofu and configured internally with Ansible.
- Kubernetes installation is not delegated to Flux because Flux requires a working cluster.
- DNS configuration is not hosted inside Kubernetes, keeping basic networking independent of
  the cluster.
- Existing resources require an explicit adoption phase.
- Public examples and tests must not depend on production inventory or addresses.
