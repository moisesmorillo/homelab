# Public repository boundary

## Threat model

Private addressing does not make an internal service Internet-reachable. Publication can still
reduce the work required for reconnaissance by correlating endpoints, roles, usernames,
software, management surfaces, physical placement, VPN access, and recovery behavior.

This project assumes its architecture and source code are public. Security must come from
network policy, timely patching, strong authentication, least privilege, and tested recovery;
it must not depend on hiding the implementation.

## Data that stays private

Do not commit any of the following:

- live IP addresses, subnets, routes, local domains, or DHCP/DNS assignments;
- production hostnames, login users, production group membership, environment-specific group
  names, or SSH key paths;
- device models tied to roles, physical locations, VM/container IDs, storage, or bridges;
- current health, versions, management URLs or ports, VPN routes, ACLs, or exposure state;
- public WAN addresses, dynamic-DNS names, account identifiers, or certificate names;
- credentials, tokens, private keys, decrypted files, kubeconfigs, or state files.

Operational values belong in a private sibling overlay. Secrets still belong in a secret
manager or an encrypted store rather than in plaintext overlay files.

## Data that may remain public

- abstract topology and trust boundaries;
- reusable roles, tasks, templates, and fail-safe rollback logic;
- generic technology choices and ownership decisions;
- parameterized runbooks without deployed values;
- examples using IETF documentation networks and `.invalid` DNS names;
- CI, linting, tests, and security policy.

## Enforcement

`make public-boundary` inspects tracked files and unignored files intended for the next commit.
It rejects reserved private paths, live-mode switches, enabled apply defaults, and IPv4 literals
outside the documentation ranges. It also rejects common numeric VM/container identifiers.
`.gitignore` is only a secondary guard because force-adding a file can bypass it.

Automation cannot determine whether a plausible-looking example preserves a private hostname,
placement, suffix scheme, or role association. A semantic review of examples and diagrams is a
required publication step.

This check protects the current tree, not Git history. Removing a value in a new commit does not
remove it from older commits, tags, forks, caches, or existing clones. If historical topology or
an external locator must be retracted, rotate the external identifier first and publish a new
sanitized repository from a clean root. History rewriting alone cannot revoke copied data.
