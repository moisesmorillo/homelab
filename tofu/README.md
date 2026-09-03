# OpenTofu

OpenTofu manages Proxmox virtual resources such as VMs and containers, CPU, memory, disks,
bridges, and virtual network interfaces. Ansible manages the operating systems inside those
resources.

## Adopting existing resources

An existing resource must be imported rather than declared and applied as though it were new.
The production resource identifiers and current configuration belong in the private operator
overlay, not in this public repository.

Before writing a resource block, capture the following in the private inventory:

- the API endpoint and target node identifiers;
- the effective storage and bridge configuration;
- the complete configuration of the resource to be adopted;
- any source image or template identifiers and properties;
- a least-privilege API credential supplied outside Git;
- an encrypted state backend with tested backups.

Use this adoption sequence:

1. Model the existing resource exactly as observed.
2. Import it using the identifier supplied by the private operator overlay.
3. Produce and review a no-change plan.
4. Take and verify any required workload and data backups.
5. Permit mutations only after the no-change baseline and backups have been approved.

If the provider cannot adopt a property without replacing the resource, document the limitation
or ignore that property temporarily. A plan that proposes unexpected replacement is a blocker,
not an approval to proceed.

## Shared inputs

OpenTofu can read network data from an operator-supplied file without duplicating it in the root
module:

```hcl
variable "network_config_path" {
  description = "Path to the private network configuration overlay"
  type        = string
}

locals {
  homelab = yamldecode(file(var.network_config_path)).homelab
}
```

The `environments/homelab` implementation will be added only after the existing infrastructure
has been inventoried and its adoption plan has been reviewed.
