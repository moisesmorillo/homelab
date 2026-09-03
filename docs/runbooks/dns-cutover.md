# DNS cutover

This runbook defines a safe sequence. Supply every environment-specific value from the external
private overlay; placeholders in this document are not executable values.

## Preconditions

- The existing resolver is backed up, updated, and protected by non-default credentials.
- `<primary-dns-address>` and `<secondary-dns-address>` are reserved and conflict-free.
- The active DHCP service still advertises the previously verified resolver set.
- Time synchronization and outbound resolution work from both DNS hosts.
- Administrative interfaces are restricted to the intended management network or authenticated
  private access path.

## Sequence

1. Install or adopt the primary DNS service with a pinned version.
2. Verify that it listens only on the intended service and management interfaces.
3. Join the secondary service using the DNS platform's supported synchronization mechanism.
4. Configure the private local zone, forwarders, caching policy, and conservative blocklists.
5. Test direct queries against both resolver addresses from more than one client.
6. Stop each resolver in turn and confirm the other continues serving expected responses.
7. Change one test client's DHCP scope or reservation to advertise the target resolver set.
8. Verify positive and negative responses, DNSSEC behavior, latency, and failover.
9. Expand the DHCP change gradually and observe a full lease-renewal window.

## Rollback criteria

- Sustained resolution failures or unacceptable latency.
- Inconsistent A, AAAA, negative-cache, or DNSSEC behavior.
- Unstable synchronization between resolver instances.
- An administrative interface is exposed outside the intended access boundary.

Rollback restores the previously captured DHCP resolver set. Do not remove either DNS instance
until client leases have converged and the rollback window has closed.
