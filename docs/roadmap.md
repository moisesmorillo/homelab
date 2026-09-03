# Roadmap

This public roadmap describes capabilities and safety gates. Environment-specific progress,
inventory, addresses, and hardware decisions belong in the external private overlay.

## 1. Declarative foundation

- [x] Define the IPAM schema and ownership boundaries.
- [x] Create a guarded `systemd-networkd` migration role.
- [x] Create a minimal, renderable Kustomize base.
- [ ] Configure SOPS with the operator's public age recipient.
- [ ] Pin Kubernetes, Flux, DNS platform, and provider versions.

## 2. Live-state capture

- [ ] Back up DNS configuration and data.
- [ ] Inventory the existing Kubernetes cluster, package releases, custom resources, storage,
  and secrets.
- [ ] Verify hosts, network devices, and unused target addresses.
- [ ] Verify remote-access routes, ACLs, and tags.
- [ ] Record evidence in private documentation.

## 3. Edge-node networking

- [ ] Render and review the proposed network change without applying it.
- [ ] Add management and service addresses while preserving the legacy recovery address.
- [ ] Verify connectivity from an independent controller and after a controlled reboot.

## 4. DNS

- [ ] Adopt the existing DNS service without recreating it.
- [ ] Deploy the complementary DNS service with a pinned version.
- [ ] Configure synchronization, local zones, forwarders, caching, and conservative blocklists.
- [ ] Test each resolver independently and test failover.
- [ ] Advertise the target resolvers through DHCP only after rollback is proven.

## 5. Kubernetes and Flux

- [ ] Back up the existing cluster or explicitly confirm it is disposable.
- [ ] Install a pinned Kubernetes distribution through Ansible.
- [ ] Bootstrap Flux.
- [ ] Reintroduce remote access with encrypted credentials and conservative defaults.
- [ ] Remove the legacy management address only after the cutover is stable.

## 6. Virtualization and gateway

- [ ] Model one existing guest and import it with a no-change plan.
- [ ] Adopt remaining guests gradually.
- [ ] Select and validate the future gateway platform.
- [ ] Move bridge mode, firewall, DHCP, and VLAN ownership in an independent maintenance window.
