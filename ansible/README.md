# Ansible

Ansible manages Linux hosts. OpenTofu owns virtual hardware, while Flux owns resources inside
Kubernetes.

The controller uses Python 3.12 or newer. Managed hosts must provide Python 3.9 or newer for the
pinned `ansible-core` release; verify this before any operational run.

## Public inventories

The default `inventory/ci/hosts.yaml` inventory intentionally contains no hosts. It exists so
syntax checks and linting are safe in a public clone. `inventory/example` contains sanitized,
non-routable examples and is never selected automatically.

Live network data and inventory belong in the private overlay, which defaults to the sibling
directory `../homelab-local`:

```text
../homelab-local/config/network.yaml
../homelab-local/ansible/inventory/production/hosts.yaml
../homelab-local/ansible/inventory/production/host_vars/
```

Private keys and passwords must not be stored in either inventory. SSH access should already
work through `ssh-agent` or `~/.ssh/config`.

## Safe execution

Run operational commands from the repository root. Planning and applying both require the
overlay path, one exact inventory host, and the private environment ID:

```bash
make network-plan \
  OVERLAY_DIR=../homelab-local \
  TARGET_HOST=sample-node-a \
  CONFIRM=your-private-environment-id
```

Only `make network-apply` enables mutation. The playbook and role independently reject public
example data, missing confirmations, and broad or absent Ansible limits.
