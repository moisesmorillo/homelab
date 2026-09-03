# Edge-node network migration

This runbook adds a management address and an optional service address while preserving a legacy
recovery address. Real inventory, addresses, interface names, and paths come from the external
private overlay.

Placeholder vocabulary:

```text
<legacy-address>       current recovery endpoint
<management-address>   target host and cluster endpoint
<service-address>      optional dedicated service endpoint
<gateway-address>      currently verified default gateway
<interface-name>       active wired interface
<overlay-directory>    external private overlay root
<inventory-host>       exact host selected from the private inventory
<environment-id>       private environment confirmation string
```

## 1. Preconditions

- Confirm target addresses are unused by checking the authoritative lease or neighbor tables
  and probing from more than one system.
- Confirm SSH to `<legacy-address>` works with the same identity Ansible will use.
- Confirm the interface, renderer, default route, and active configuration match the private
  inventory.
- Keep a second session open through the legacy address.
- Have local or serial-console access in case automated recovery fails.

## 2. Validate the repository and private overlay

From the repository root:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-dev.txt
make validate
```

Validate the private paths and exact host selection without contacting the managed host:

```bash
OVERLAY_DIRECTORY=../homelab-local
INVENTORY_HOST=sample-node-a
ENVIRONMENT_ID=your-private-environment-id

make overlay-check \
  OVERLAY_DIR="$OVERLAY_DIRECTORY" \
  TARGET_HOST="$INVENTORY_HOST" \
  CONFIRM="$ENVIRONMENT_ID"
```

## 3. Simulate

```bash
make network-plan \
  OVERLAY_DIR="$OVERLAY_DIRECTORY" \
  TARGET_HOST="$INVENTORY_HOST" \
  CONFIRM="$ENVIRONMENT_ID"
```

The rendered change must contain only the addresses, gateway, DNS servers, search domains, and
interface declared in the reviewed private overlay. Stop if the diff removes the active recovery
path or contains an unexpected route.

## 4. Apply with automatic rollback

Use the dedicated apply target only during a controlled maintenance window:

```bash
make network-apply \
  OVERLAY_DIR="$OVERLAY_DIRECTORY" \
  TARGET_HOST="$INVENTORY_HOST" \
  CONFIRM="$ENVIRONMENT_ID"
```

Before changing the active interface, the role:

1. acquires an atomic migration lock;
2. saves the immediately preceding renderer configuration with restrictive permissions;
3. installs a local rollback helper;
4. arms a transient rollback timer;
5. reloads the network renderer;
6. verifies expected addresses, the default gateway, controller reachability, and the trusted
   SSH host key;
7. atomically commits only after every check passes, then stops the rollback units and releases
   the lock.

If the rollback helper wins the decision first, Ansible cannot report success or overwrite that
recovery. An automatic rollback leaves a persistent rollback decision that blocks another run
until an operator inspects it using [`recovery.md`](recovery.md).

If Ansible loses its connection, do not cancel recovery or immediately rerun the playbook. Wait
for the configured timer, reconnect through the legacy address, and inspect the rollback state.

## 5. External verification

From an independent system on the intended management network:

```bash
LEGACY_ADDRESS=192.0.2.63
MANAGEMENT_ADDRESS=192.0.2.32
SERVICE_ADDRESS=192.0.2.40
OPERATOR=example-user

ping "$LEGACY_ADDRESS"
ping "$MANAGEMENT_ADDRESS"
ping "$SERVICE_ADDRESS"
ssh "$OPERATOR@$MANAGEMENT_ADDRESS"
```

On the edge node, inspect the private interface and renderer values:

```bash
INTERFACE_NAME=eth0

ip -br -4 address show dev "$INTERFACE_NAME"
ip -4 route
networkctl status "$INTERFACE_NAME"
```

Repeat all checks after a controlled reboot.

## 6. Retire the legacy address

Do not remove the legacy address in the initial migration. First verify DNS, Kubernetes,
configuration reconciliation, SSH, inventory, and reboot behavior through the management
address. Removing the legacy address is a separate reviewed change executed from the replacement
management path with the same rollback mechanism.

## Manual recovery

Do not run a persistent rollback helper blindly. Compare the active renderer configuration with
the saved snapshot and confirm that the snapshot is the intended recovery state. Follow
[`recovery.md`](recovery.md), using the helper path recorded in the private overlay.
