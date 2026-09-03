# Addressing plan

The tracked schema and documentation-only sample live in
[`../config/network.example.yaml`](../config/network.example.yaml). The real address plan belongs
in the external private overlay.

## Documentation example

The addresses below use `192.0.2.0/24` (`TEST-NET-1`), reserved by RFC 5737 for documentation.
They are examples only and must not be copied into a deployed network.

| Purpose | Example range or address |
| --- | --- |
| Documentation network | `192.0.2.0/24` |
| Gateway | `192.0.2.254` |
| Dynamic clients | `192.0.2.128-192.0.2.223` |
| Network services | `192.0.2.8-192.0.2.15` |
| Managed nodes | `192.0.2.32-192.0.2.47` |
| Virtual infrastructure | `192.0.2.48-192.0.2.55` |
| Migration examples | `192.0.2.56-192.0.2.63` |

Example allocations illustrate intent rather than real hosts:

| Example address | Role | Lifecycle |
| --- | --- | --- |
| `192.0.2.10` | Primary example resolver | Example only |
| `192.0.2.11` | Secondary example resolver | Example only |
| `192.0.2.32` | Sample management endpoint | Example only |
| `192.0.2.36` | Sample control-plane endpoint | Example only |

The pool boundaries, suffixes, names, placements, and role associations are deliberately
invented. They do not preserve the structure of the private allocation plan.

## Allocation rules

- The DHCP pool must not overlap static allocations.
- The currently advertised DNS servers must be discovered before changing DHCP.
- Target DNS servers are advertised only after direct queries, failover, and rollback have been
  tested.
- Management and service addresses have distinct purposes even when they temporarily share a
  host.
- Pod and service networks must not overlap the LAN, VPN routes, or upstream networks.
- Removing a legacy management address is a separate, explicit change after all consumers use
  the replacement address.

Exact LAN, pod, service, and VPN routes must be supplied by the private configuration and
validated against the environment before automation runs.
