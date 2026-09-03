# Kubernetes rebuild

This document is a safety gate, not authorization to erase an existing cluster. Exact addresses,
routes, versions, and inventory come from the external private overlay.

## Before rebuilding

- Export namespaces, custom resources, package releases, storage definitions, secrets, and
  remote-access configuration.
- Back up the datastore and persistent volume contents with a restore test appropriate to the
  installed version.
- Record which data is disposable and which data has a verified, restorable backup.
- Pin the Kubernetes distribution version and document its checksum or distribution channel.
- Confirm that `<control-plane-address>` survives a reboot.
- Confirm that both external DNS services remain available throughout the rebuild.
- Validate that `<pod-cidr>` and `<service-cidr>` do not overlap the LAN, VPN, or upstream routes.

## Target configuration template

```yaml
node-ip: <control-plane-address>
advertise-address: <control-plane-address>
tls-san:
  - <control-plane-address>
cluster-cidr: <pod-cidr>
service-cidr: <service-cidr>
```

The administrative kubeconfig must have mode `0600`; do not expose it globally with mode
`0644`.

## Sequence

1. Capture evidence and complete all backups.
2. Run destructive removal only after explicit confirmation for the identified cluster.
3. Install the pinned Kubernetes version through an idempotent Ansible role.
4. Verify the API, cluster DNS, storage, and a controlled node reboot.
5. Bootstrap Flux and reconcile infrastructure.
6. Restore applications one at a time and verify their data.
7. Remove the legacy management address only after repeated health and reboot checks.

Add destructive automation only after the private live-state inventory and restore plan are
complete.
