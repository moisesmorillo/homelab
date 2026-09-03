# Recovery

Exact hosts, addresses, unit names, file paths, and backup locations belong in the external
private overlay. This runbook describes the recovery decisions that apply across environments.

## Repository recovery

- Inspect historical content without modifying the active working tree.
- Prefer a temporary worktree or a read-only object inspection command.
- Never perform a destructive reset over uncommitted work.
- Keep private overlays and encrypted backups separate from repository history.

## Edge node without network access

1. Connect locally or through the documented out-of-band console.
2. Compare the active renderer configuration with the rollback snapshot.
3. Confirm that the snapshot represents the intended recovery state.
4. Run the installed rollback helper only after that comparison.
5. Verify addresses, the default route, gateway reachability, and SSH before rebooting.

An automatic rollback deliberately leaves a persistent rollback decision so a later run cannot
overwrite the snapshot before review. A failure before the timer is armed may leave an empty
migration lock instead. Inspect the active file, snapshot, decision, timer, service, and journal
before clearing either condition.

If the rollback service is failed, review its journal first. Reset its failed state only after
the recovered network has been verified; otherwise the next preflight should remain blocked.

## DNS recovery

- Keep encrypted DNS exports outside both resolver instances.
- Record the previously advertised resolver set before changing DHCP.
- Restore that resolver set if the new pair fails validation.
- Do not recreate an adopted resolver until a tested backup exists.

## Kubernetes recovery

- Exported manifests are not a backup of persistent data.
- Restore the datastore and volumes according to the pinned version's tested procedure.
- External DNS and gateway services must remain independent of the cluster throughout recovery.
