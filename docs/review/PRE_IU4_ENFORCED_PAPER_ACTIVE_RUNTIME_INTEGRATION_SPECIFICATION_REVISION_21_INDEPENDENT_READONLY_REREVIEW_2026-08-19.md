# PRE-IU4 Enforced-Paper Active Runtime Integration Specification — Revision 21 Independent Read-Only Rereview

**Review-ID:** `IU4-ENFORCED-PAPER-ACTIVE-RUNTIME-INTEGRATION-SPECIFICATION-REVISION-21-INDEPENDENT-READONLY-REREVIEW`
**Review date:** `2026-08-19`
**Review mode:** fully independent, adversarial, read-only rereview
**Canonical repository:** `/home/benja/projects/sniper-bot`
**Verdict:** `READY`
**Finding counts:** `BLOCKER 0 / HIGH 0 / MEDIUM 0 / LOW 0`

## 1. Decision

Revision 21 of the IU4 Enforced-Paper Active Runtime Integration Specification is specification-implementation-ready.

```text
SPECIFICATION_IMPLEMENTATION_READY:YES
IMPLEMENTATION_AUTHORIZED:NO
R3_FINAL_ATTESTATION_BOUND:NO
```

The distinction is controlling:

- `SPECIFICATION_IMPLEMENTATION_READY:YES` means this rereview found no unresolved specification defect at BLOCKER, HIGH, MEDIUM, or LOW severity.
- `IMPLEMENTATION_AUTHORIZED:NO` means this record does not authorize implementation, activation, exchange connectivity, live operation, or any later governance step.
- The required R3 terminal handoff, frozen postrun validation, final R3 PASS, and identity binding remain outstanding.

No closure credit was taken from the Revision 20 resolution or from Revision 21’s own assertions. The Revision 20 HIGH finding was re-derived independently against the executable Linux mechanism, failure states, preservation chain, and end-to-end completion obligations.

## 2. Exact reviewed identities

### 2.1 Target specification

| Field | Value |
|---|---|
| Path | `/home/benja/projects/sniper-bot/docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md` |
| Expected revision | `21` |
| Observed revision | `21` |
| Expected SHA-256 | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` |
| Observed SHA-256 | `ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0` |
| Expected lines | `4605` |
| Observed lines | `4605` |
| Identity result | `MATCH` |

### 2.2 Controlling Revision 20 rereview resolution

| Field | Value |
|---|---|
| Path | `/home/benja/projects/sniper-bot/docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_20_REREVIEW_RESOLUTION_2026-08-19.md` |
| Expected SHA-256 | `bad8c90f1409f1d2893db204d6b5abdf9e0608c7aeb42227479191f41e828888` |
| Observed SHA-256 | `bad8c90f1409f1d2893db204d6b5abdf9e0608c7aeb42227479191f41e828888` |
| Expected lines | `518` |
| Observed lines | `518` |
| Identity result | `MATCH` |

### 2.3 Controlling Revision 20 independent rereview

| Field | Value |
|---|---|
| Path | `/home/benja/projects/sniper-bot/docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_20_INDEPENDENT_READONLY_REREVIEW_2026-08-19.md` |
| Expected SHA-256 | `c40e5af0fb499d8611097409946bd38f2b813ab10a0b0425e9071c4712868338` |
| Observed SHA-256 | `c40e5af0fb499d8611097409946bd38f2b813ab10a0b0425e9071c4712868338` |
| Expected lines | `401` |
| Observed lines | `401` |
| Identity result | `MATCH` |

### 2.4 Repository identity observed for the review

| Field | Value |
|---|---|
| Local `HEAD` / `main` | `c7ce0452aa2ccbf08c462784d68fa07b3dfe9595` |
| Observed `origin/main` | `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a` |
| Left/right divergence | `0 / 6` |
| Review basis | exact file identities above, not an inferred branch label |

The worktree already contained unrelated untracked artifacts. They were treated as pre-existing user-owned state and were not modified, staged, removed, normalized, or incorporated into the review result.

## 3. Authorities and preservation inputs

The rereview used the following controlling authority set:

- `AGENTS.md`
- `docs/LIVE_DESIGN_L0_L1_VERSIONING_AND_REVIEW.md`
- `docs/LIVE_DESIGN_L0_MINIMAL_LIVE_LOOP.md`
- `docs/LIVE_DESIGN_L0_STATE_MODEL.md`
- `docs/LIVE_DESIGN_L1C_GUARD_AND_KILLSWITCH_RULES.md`
- `docs/LIVE_DESIGN_L1D_RESTART_AND_RECOVERY_PROTOCOL.md`
- the controlling PEE specification
- the controlling ownership decision
- the Revision 15 through Revision 20 independent-review finding chain
- the applicable resolution lineage, including the Revision 18, Revision 19, and controlling Revision 20 resolutions

The following authority identities were independently observed during the review:

| Authority | SHA-256 |
|---|---|
| L0/L1 Versioning and Review | `3142ed71…494e8` |
| L0 Minimal Live Loop | `8bfd1bd7…555d` |
| L0 State Model | `3c836ecc…1490` |
| L1C Guard and Killswitch Rules | `15617c95…ae40` |
| L1D Restart and Recovery Protocol | `1e7b408f…2e94` |
| PEE authority | `5df91de8…dfa4` |
| Ownership authority | `e79989dd…2478` |

The abbreviated authority hashes above are recorded only as review cross-checks. The exact admission identity for this rereview is the full target-specification SHA-256 stated in section 2.1.

The older independent-review records were checked with these observed identities:

| Review | SHA-256 | Lines |
|---|---:|---:|
| Revision 15 independent review | `8276a4…c477` | `282` |
| Revision 16 independent review | `85068c…80df` | `330` |
| Revision 17 independent review | `b976df…33d8` | `361` |
| Revision 18 independent review | `8efb96…0427` | `482` |
| Revision 19 independent review | `256013…f4ca` | `444` |
| Revision 20 independent review | `c40e5af0fb499d8611097409946bd38f2b813ab10a0b0425e9071c4712868338` | `401` |

Applicable older resolution identities observed in the chain included:

| Resolution | SHA-256 | Lines |
|---|---:|---:|
| Revision 15 resolution | `d4377470…5879` | `342` |
| Revision 16 resolution | `25a94f…e041` | `321` |
| Revision 17 resolution | `5b56d2…fce2` | `363` |
| Revision 18 resolution | `6134a0…1af9` | `486` |
| Revision 19 resolution | `edc0ca…92fa0` | `561` |
| Revision 20 resolution | `bad8c90f1409f1d2893db204d6b5abdf9e0608c7aeb42227479191f41e828888` | `518` |

No older finding was considered closed merely because a resolution document said so. Preservation was checked against the operative Revision 21 mechanism.

## 4. Method

The review was performed adversarially and without implementation activity.

The method was:

1. Read `AGENTS.md` completely before repository work.
2. Establish the exact repository, target, controlling review, and controlling resolution identities.
3. Read the entire 4,605-line Revision 21 specification.
4. Read the entire controlling Revision 20 review and resolution.
5. Read the applicable L0/L1, PEE, and ownership authorities.
6. Trace the relevant Revision 15–20 finding and resolution lineage.
7. Reconstruct the six-stage phase machine independently from the described syscall-visible transitions.
8. Reconstruct the three-control-socket ownership and transition mapping.
9. Derive every phase’s runtime-socket-creation gate and send gate without trusting the specification’s summary tables.
10. Check the exact `shutdown(2)` allowlists against role, FD, direction, socket identity, phase, session, cgroup, task identity, and atomic state transition.
11. Check that an early Guard operation is rejected before any grant or phase mutation.
12. Check that Attestor and Persistence grants do not themselves open a runtime send gate.
13. Check bootstrap ordering, socket tagging, cookie binding, map freezing, seccomp installation, and post-filter evidence.
14. Check the durable-OPEN continuation across file sync, directory sync where required, readback, ledger binding, state revalidation, and grant.
15. Exercise crash, stop, syscall-return-loss, duplicated-call, stale-FD, wrong-cookie, wrong-role, wrong-session, and wrong-phase cases as specification-state traces.
16. Reconstruct the complete six-channel scalar protocol and verify that every permitted direction remains denied through phases 0–4.
17. Recheck preservation of the older finding closures and the L0/L1 kill, recovery, restart, and ownership rules.
18. Use only primary Linux sources for Linux kernel, BPF, LSM, seccomp-adjacent syscall, and socket semantics.
19. Perform no write-capable test, runtime mutation, staging, commit, fetch, push, or build-bundle action.

This was a specification rereview. It was not a kernel qualification, runtime test, implementation audit, deployment exercise, or live-readiness authorization.

## 5. Primary Linux sources and semantic conclusions

Linux semantics were checked against upstream kernel source and official kernel documentation, including:

- Linux `v6.18` `net/socket.c`
- Linux `v6.18` `kernel/pid.c`
- Linux `v6.18` `kernel/bpf/syscall.c`
- Linux `v6.18` `include/linux/lsm_hook_defs.h`
- the official BPF instruction-set documentation for atomic operations and `CMPXCHG`
- the upstream kernel change introducing the relevant AF_UNIX rights/prequeue behavior
- the upstream `bpftool map` documentation for frozen-map behavior

Primary-source locations:

- [Linux v6.18 `net/socket.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/net/socket.c?h=v6.18)
- [Linux v6.18 `kernel/pid.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/kernel/pid.c?h=v6.18)
- [Linux v6.18 `kernel/bpf/syscall.c`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/kernel/bpf/syscall.c?h=v6.18)
- [Linux v6.18 `lsm_hook_defs.h`](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/include/linux/lsm_hook_defs.h?h=v6.18)
- [Official BPF instruction-set documentation](https://docs.kernel.org/bpf/standardization/instruction-set.html)
- [Upstream `bpftool-map` documentation](https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/tree/tools/bpf/bpftool/Documentation/bpftool-map.rst?h=v6.18)

The primary-source check established the following:

| Required semantic | Independent result |
|---|---|
| LSM can reject `shutdown` before protocol shutdown mutates the socket | Confirmed: `security_socket_shutdown()` precedes the protocol operation |
| LSM can reject a send before protocol send execution | Confirmed: `security_socket_sendmsg()` is called before the protocol send |
| Socket creation can be inspected/tagged before publication to the caller | Confirmed by the socket creation/post-create/FD-publication path |
| `pidfd_getfd` reception traverses the file-receive security path before installation | Confirmed through `receive_fd()` and `security_file_receive` ordering |
| Required LSM hooks exist | Confirmed for `file_receive`, `unix_stream_connect`, `socket_post_create`, `socket_sendmsg`, `socket_setsockopt`, and `socket_shutdown` |
| A writable map FD is required to freeze the map | Confirmed |
| A frozen map blocks later user-space update/delete operations through BPF syscalls | Confirmed |
| Freezing does not remove write capability from already loaded BPF programs | Confirmed; this is required by the specification’s enforcement design |
| Atomic 64-bit compare-and-exchange is expressible in BPF | Confirmed by the BPF ISA `CMPXCHG` definition |
| Compare-and-exchange can make the phase change conditional on one exact predecessor | Confirmed |
| Failed compare-and-exchange leaves the authoritative phase unchanged | Confirmed |
| The three distinct shutdown-triggered transitions are implementable at the LSM hook | Confirmed |
| Read-only reopening after freeze can remove a writable userspace control-plane handle while retaining BPF-program enforcement updates | Confirmed as the required design separation |

The local review host reported a Linux/WSL kernel in the `6.18` series, and its installed UAPI header exposed `BPF_CMPXCHG` and `BPF_MAP_FREEZE`. This observation was not treated as target-host certification and did not replace the primary-source analysis.

## 6. Independent re-derivation of Revision 20 HIGH finding closure

### 6.1 Reconstructed authoritative phase machine

Revision 21 defines one authoritative six-state phase word:

| Value | Phase |
|---:|---|
| `0` | `LISTENER_HANDOFF` |
| `1` | `LISTENER_RECEIVED` |
| `2` | `HANDOFF_REVOKED_GRANTED` |
| `3` | `BOOTSTRAP` |
| `4` | `OPEN_DURABLE_GRANTED` |
| `5` | `RELEASED` |

There are exactly five forward transitions:

| Transition | Authorized actor and operation | Required predecessor | Successor |
|---|---|---:|---:|
| T1 | Broker completes the listener reception through the controlled `file_receive` path | `0` | `1` |
| T2 | Attestor performs `shutdown(attestor_grant_fd, SHUT_WR)` | `1` | `2` |
| T3 | Guard performs `shutdown(phase_fd, SHUT_RD)` | `2` | `3` |
| T4 | Persistence Owner performs `shutdown(persistence_grant_fd, SHUT_WR)` | `3` | `4` |
| T5 | Guard performs `shutdown(phase_fd, SHUT_RDWR)` | `4` | `5` |

Each transition is conditioned on the full controlling tuple, not merely the `shutdown` direction:

- expected phase,
- exact role/task identity,
- exact TID or other required process identity,
- expected cgroup,
- active session identity,
- exact tagged control socket,
- exact socket cookie,
- exact FD permitted by the role-local seccomp filter,
- exact `how` value,
- atomic compare-and-exchange from the one permitted predecessor.

No other role, socket, cookie, FD, phase, or shutdown direction can perform a successful transition.

### 6.2 Three control sockets and separated trust domains

The transition design uses three distinct control sockets:

1. the Attestor grant socket,
2. the Guard phase socket,
3. the Persistence Owner grant socket.

They are not interchangeable.

The separation is material:

- The Attestor is trusted for the listener-handoff revocation evidence and can issue only the phase-1-to-phase-2 grant.
- The Guard consumes the completed Attestor grant to enter bootstrap and later consumes the completed persistence grant to release the session.
- The Persistence Owner is trusted for the durable-OPEN continuation and can issue only the phase-3-to-phase-4 grant.
- The BPF LSM enforcement layer remains responsible for identity, socket, cookie, phase, syscall, and atomic predecessor enforcement.
- Neither Attestor nor Persistence Owner can directly perform the Guard’s phase transition.
- The Guard cannot manufacture either external grant.
- Possession of one control socket does not satisfy the identity or cookie checks for another.

This is a genuine division between Attestor, Persistence Owner, Guard, and enforcement TCB responsibilities, rather than a relabeling of one shared authority.

### 6.3 Exact role-local `shutdown` allowlists

The final seccomp posture allows only these grant/phase operations:

| Role | Allowed operation |
|---|---|
| Attestor | `shutdown(attestor_grant_fd, SHUT_WR)` |
| Persistence Owner | `shutdown(persistence_grant_fd, SHUT_WR)` |
| Guard, bootstrap entry | `shutdown(phase_fd, SHUT_RD)` |
| Guard, release | `shutdown(phase_fd, SHUT_RDWR)` |

All other `shutdown` combinations are denied by the role’s syscall filter or rejected by the LSM policy.

The LSM check remains necessary because seccomp’s FD-number comparison alone cannot prove the socket object, socket cookie, phase, session, cgroup, or one-time predecessor. Conversely, the final seccomp filter limits the syscall surface even if a role retains an unrelated FD. The two layers are complementary.

### 6.4 Early Guard rejection occurs before grant mutation

The critical adversarial trace is an otherwise correct Guard call made before the Attestor grant:

```text
phase = LISTENER_RECEIVED (1)
caller = expected Guard
socket = expected phase socket
cookie = expected phase-socket cookie
cgroup/session = expected
operation = shutdown(phase_fd, SHUT_RD)
```

The only valid predecessor for the bootstrap-entry compare-and-exchange is phase `2`.

Therefore the atomic compare-and-exchange fails while the authoritative phase is `1`. The LSM hook returns an error before the protocol `shutdown` operation. The socket is not shut down, the phase is not advanced, no grant is synthesized, and no runtime creation or send gate opens.

The same reasoning applies to a premature Guard release call:

```text
phase != OPEN_DURABLE_GRANTED (4)
operation = shutdown(phase_fd, SHUT_RDWR)
```

The expected predecessor is absent, so the phase remains unchanged and protocol shutdown does not occur.

This closes the ordering defect independently: the Guard cannot convert an anticipated grant into an effective grant by calling its own transition early.

### 6.5 Grants do not open their own send gate

The Attestor grant changes phase `1` to phase `2`.

Phase `2`:

- does not permit runtime sends,
- does not permit runtime socket creation,
- is not `RELEASED`,
- merely makes the Guard’s exact bootstrap-entry transition eligible.

The Persistence Owner grant changes phase `3` to phase `4`.

Phase `4`:

- does not permit runtime sends,
- does not permit new runtime socket creation,
- is not `RELEASED`,
- merely makes the Guard’s exact release transition eligible.

Thus neither external grant opens the operational send gate. Only the Guard’s final phase-4-to-phase-5 transition produces `RELEASED`, and that transition is impossible until the Persistence Owner has completed the durable-OPEN continuation.

### 6.6 Runtime-socket creation gate

The independently reconstructed runtime-socket-creation rule is:

| Phase | New runtime `SOCK_SEQPACKET` socket creation |
|---:|---|
| `0` — `LISTENER_HANDOFF` | Denied |
| `1` — `LISTENER_RECEIVED` | Denied |
| `2` — `HANDOFF_REVOKED_GRANTED` | Denied |
| `3` — `BOOTSTRAP` | Allowed only for the specified bootstrap creator/path |
| `4` — `OPEN_DURABLE_GRANTED` | Denied |
| `5` — `RELEASED` | Denied |

The gate is intentionally a one-phase construction window, not a permission that remains open after release.

The construction sequence binds the runtime endpoints before operational release:

- creation in `BOOTSTRAP`,
- expected endpoint ownership,
- per-socket tag initialization,
- cookie capture and association,
- required option state,
- transition from `INIT` to `SEALED`,
- ancillary-rights prohibition,
- final role filters,
- post-filter snapshot/evidence,
- no additional runtime socket creation after phase `3`.

Consequently, later compromise cannot manufacture an additional runtime channel merely because the system has reached `RELEASED`.

### 6.7 Send gate across phases 0–4

The send gate is closed for all protected runtime channels in every phase before `RELEASED`:

| Phase | Protected runtime sends |
|---:|---|
| `0` | Denied |
| `1` | Denied |
| `2` | Denied |
| `3` | Denied |
| `4` | Denied |
| `5` | Allowed only for the exact sealed socket, cookie, sender role, direction, session, message class, and scalar protocol path |

This prevents:

- sends during listener handoff,
- sends after listener receipt but before revocation attestation,
- sends after the Attestor grant but before Guard bootstrap entry,
- sends during construction,
- sends after durable-OPEN grant but before Guard release.

Phase `5` is necessary but not sufficient. The endpoint tag, socket cookie, owner, sender direction, cgroup/session binding, and permitted scalar message set must also match.

### 6.8 Map construction and freeze order

The authoritative phase map is constructed with the required update capability, used to load and verify the enforcing programs, and then frozen against userspace mutation.

The reviewed order is:

1. create the map with the intended base flags,
2. initialize the authoritative state,
3. load the BPF programs that require program-side update access,
4. freeze the map through the writable creator FD,
5. close the writable creator handle,
6. reopen or retain only the specified read-only userspace view,
7. use the already loaded BPF programs for the tightly checked atomic phase transitions.

The design does not make the incorrect assumption that `BPF_MAP_FREEZE` prevents BPF-program writes. It uses freeze to remove ordinary userspace mutation while retaining the program-side enforcement path.

No role receives a userspace capability to write arbitrary phase values.

### 6.9 Bootstrap-order closure

The effective order is:

1. listener handoff begins in phase `0`,
2. controlled Broker receipt advances to phase `1`,
3. required source-side close/revocation evidence completes,
4. Attestor grants phase `2`,
5. Guard consumes that grant and enters phase `3`,
6. runtime socketpairs are created and sealed only in phase `3`,
7. final role filters and post-filter evidence are established,
8. durable OPEN continuation completes,
9. Persistence Owner grants phase `4`,
10. Guard consumes that grant and advances to phase `5`,
11. roles may proceed only after their specified external phase/open consistency checks.

No phase permits both unrestricted construction and operational sending. No grant actor can bypass the Guard, and the Guard cannot bypass either grant actor.

### 6.10 Revision 20 HIGH conclusion

The Revision 20 HIGH issue is independently closed.

Closure does not depend on prose intent. It follows from the combined executable invariants:

- one authoritative six-state word,
- exactly five predecessor-bound forward transitions,
- three non-interchangeable tagged control sockets,
- exact socket cookies,
- role-local seccomp allowlists,
- LSM checks before protocol mutation,
- atomic compare-and-exchange,
- runtime creation only in phase `3`,
- no protected sends in phases `0` through `4`,
- external grants at phases `2` and `4` that open no send gate,
- final Guard release only from phase `4`.

**Disposition:** `V20-H1 CLOSED`.

## 7. Six-channel end-to-end preservation

The complete protected runtime protocol remains exactly six directed logical channels:

| Channel | Direction | Permitted scalar classes |
|---|---|---|
| `GB_REQUEST` | Guardian → Broker | Renewal Request; Orderly Close Request |
| `BG_CLOSE_APPROVAL` | Broker → Guardian | Close Approval |
| `BS_RENEWAL_APPROVAL` | Broker → Shim | Renewal Approval |
| `BS_CLOSE_APPROVAL` | Broker → Shim | Close Approval |
| `BW_REQUEST` | Broker → Worker | `KILL`; Prepare; Commit |
| `WB_ACK` | Worker → Broker | PrepareAck; CommitAck |

Preservation conclusions:

- All six logical channels are present.
- Their directions remain explicit and non-symmetric.
- Message classes remain scalar and enumerated.
- No protected channel permits send before phase `5`.
- Phase `5` alone does not authorize a send without the exact endpoint, cookie, owner, direction, session, and message class.
- All six socketpairs’ twelve endpoints pass through the required tag lifecycle.
- Runtime endpoints are created only in `BOOTSTRAP`.
- Runtime endpoints are sealed before release.
- Ancillary FD transfer is not an alternate runtime authority path.
- Global setsockopt enforcement prevents a later role from weakening the relevant endpoint posture.
- `file_receive` enforcement prevents an unexpected received file from becoming a bypass.
- Final TSYNC filters and post-filter evidence preserve the role-local syscall constraints.

No seventh hidden runtime channel, reverse-direction send path, generic message envelope, or FD-passing side channel is authorized by Revision 21.

## 8. Durable-OPEN continuation

The Persistence Owner’s grant is conditioned on one uninterrupted durable-OPEN continuation.

The reviewed continuation includes:

1. write the intended OPEN state and associated ledger material,
2. synchronize the file data and metadata as specified,
3. synchronize the parent directory when creation or rename durability requires it,
4. reopen or inspect through the required read-only path,
5. read back the exact bytes,
6. recompute and compare the required hash or identity,
7. validate ledger tip and anchor relationships,
8. validate session, attempt, fencing, and ownership binding,
9. re-establish the controlling state predicate after the durable operations,
10. issue the Persistence grant only from that same successful continuation.

The grant is not justified by a successful write syscall alone.

The following are therefore insufficient:

- buffered write completion without file sync,
- file sync without required parent-directory sync,
- sync without exact readback,
- readback without identity/hash comparison,
- hash comparison without ledger-tip/anchor validation,
- durable bytes belonging to a stale session or attempt,
- a prior process’s success reused after a discontinuity,
- a grant reconstructed after losing the successful continuation’s return state.

After the Persistence grant, the system is only in phase `4`; sends remain closed until the Guard consumes the grant and performs the exact phase-4-to-phase-5 transition.

## 9. Crash, stop, retry, and return-loss analysis

### 9.1 Listener receipt

If execution stops before controlled listener receipt completes, the system remains in phase `0`.

If the successful receipt transition occurs but the userspace return is lost, the authoritative phase is `1`. Runtime creation and sends remain denied. Recovery must inspect authoritative state rather than replaying the transition blindly.

### 9.2 Attestor grant

If the Attestor stops before the grant, phase remains `1`.

If the grant succeeds but its return is lost, phase is `2`. That state opens neither runtime socket creation nor sends. A retry cannot advance the phase again because the compare-and-exchange predecessor is no longer `1`.

The Guard may consume the authoritative phase-2 grant only through its own exact transition.

### 9.3 Guard bootstrap entry

If the Guard stops before consuming phase `2`, runtime creation remains denied.

If the phase-2-to-phase-3 transition succeeds but its return is lost, the authoritative state is `BOOTSTRAP`. Protected sends remain denied. Recovery may clean up or resume only under the specification’s authoritative-state rules; it may not infer release.

A repeated `SHUT_RD` transition cannot advance phase `3`, because its sole expected predecessor is phase `2`.

### 9.4 Bootstrap construction

If any creator, owner, or supervised role crashes during construction:

- sends remain denied,
- unsealed or incomplete endpoints are not operational,
- phase `3` does not imply durable OPEN,
- cleanup does not itself advance the phase,
- a new runtime socket cannot be created after leaving phase `3`.

Partial endpoint construction therefore fails closed.

### 9.5 Persistence continuation

If the Persistence Owner stops before all required sync, directory-sync, readback, ledger, session, attempt, and fencing checks complete, phase remains `3`.

If durable storage operations complete but the grant has not occurred, phase remains `3`.

If the phase-3-to-phase-4 grant succeeds but the syscall return is lost, phase is `4`. Protected sends remain denied, and the grant cannot be replayed from phase `4`.

### 9.6 Final Guard release

If the Guard stops before consuming phase `4`, protected sends remain denied.

If the phase-4-to-phase-5 transition succeeds but its return is lost, the authoritative phase is `5`. The role-local continuation must use the specified external phase/open consistency checks. It may not rely exclusively on the lost userspace return value.

A replayed final Guard shutdown cannot produce a second release because its expected predecessor was phase `4`.

### 9.7 Wrong-object and stale-object cases

The following fail closed:

- correct FD number referring to the wrong object,
- stale control FD,
- duplicated but unauthorized descriptor,
- wrong socket cookie,
- right socket in the wrong session,
- right session in the wrong cgroup,
- right role but wrong TID or process identity,
- right actor with the wrong `shutdown` direction,
- right syscall after the predecessor phase has already changed,
- send on an unsealed endpoint,
- send in the wrong logical direction,
- send of a non-enumerated message class,
- file receipt outside the specified handoff.

The failure result is no phase advance and no protocol-level operation where the LSM hook rejects before the underlying socket operation.

## 10. Preservation matrix

| Prior obligation or finding | Revision 21 preservation result | Independent basis |
|---|---|---|
| `V20-H1` | `CLOSED` | Six-state FSM, three control sockets, exact shutdown allowlists, predecessor-bound atomic transitions, phase-3-only creation, sends denied through phase `4` |
| `V19-H1` | `PRESERVED CLOSED` | Complete phase/cookie/identity enforcement remains applied to the operative paths; no direct operational bypass was reintroduced |
| `V19-H2` | `PRESERVED CLOSED` | Bootstrap and release remain separated by durable-OPEN evidence and an external persistence grant |
| `V18-H1` | `PRESERVED CLOSED` | The complete six-channel mapping and endpoint lifecycle remain enforced end-to-end |
| `V17-H1` | `PRESERVED CLOSED` | Role-local syscall restrictions, TSYNC posture, and post-filter evidence remain part of the mandatory bootstrap sequence |
| `V16-H1` | `PRESERVED CLOSED` | Session-envelope and ownership bindings remain explicit across socket, phase, persistence, and recovery checks |
| `V15-H1` | `PRESERVED CLOSED` | Capability construction and handoff remain closed against generic received-FD and post-bootstrap socket creation paths |
| `V15-B1` | `PRESERVED CLOSED` | No return to an ambiguous or unowned operational transition was found |
| Older L0/L1 closure set | `PRESERVED` | Kill, orderly close, restart, recovery, state ownership, and fail-closed rules remain mapped to the six protected channels and authoritative state |

Additional preserved invariants:

| Invariant | Result |
|---|---|
| Single authoritative owner for each state transition | Preserved |
| Decimal/wire-value stability where required | Preserved |
| Atomic V2 and return-loss/loss-cluster handling | Preserved |
| Execution-control separation | Preserved |
| Authority and ownership separation | Preserved |
| Recovery and genesis binding | Preserved |
| L0/L1 kill semantics | Preserved |
| L0/L1 restart and recovery semantics | Preserved |
| No implicit exchange or live authorization | Preserved |
| No direct pre-release operational send | Preserved |
| No post-bootstrap runtime-socket construction | Preserved |

The historical explanatory references to older direct-transition behavior are non-operative. No stale operative rule was found that authorizes the superseded path.

## 11. Contract-version consistency

The operative contract references are internally consistent:

| Contract | Version |
|---|---:|
| Runtime Control | `V15` |
| Session Envelope | `V16` |
| Guard | `V3` |
| Phase | `V3` |
| Attestor | `V1` |
| Provisioning | `V6` |
| Persistence Worker | `V8` |
| Capability | `V14` |

No version split was found that changes an operative role, direction, state value, ownership boundary, grant predicate, or recovery obligation.

## 12. Completion matrix

| Completion obligation | Result | Reason |
|---|---|---|
| Listener is received before revocation grant | PASS | Phase `0→1` precedes the Attestor transition |
| Attestor evidence precedes bootstrap | PASS | Guard bootstrap entry requires authoritative phase `2` |
| Guard cannot self-grant bootstrap | PASS | Early phase-socket shutdown fails predecessor check |
| Runtime sockets exist only from the bootstrap construction window | PASS | Creation allowed only in phase `3` |
| Runtime endpoints are sealed before release | PASS | Endpoint lifecycle and final filters precede durable grant/release |
| Durable OPEN precedes persistence grant | PASS | Grant remains in the same verified durable continuation |
| Persistence grant does not directly permit sends | PASS | Phase `4` send gate remains closed |
| Guard cannot self-grant release | PASS | Final transition requires authoritative phase `4` |
| All six channels remain closed during phases `0–4` | PASS | Global phase gate plus per-endpoint enforcement |
| Only enumerated scalar paths open in phase `5` | PASS | Sender, direction, tag, cookie, session, and message checks remain mandatory |
| Crash before any grant fails closed | PASS | No successor phase is inferred |
| Crash after a grant but before consumption fails closed | PASS | Grant phases `2` and `4` open no sends |
| Successful-transition return loss is recoverable from authoritative state | PASS | One-way CMPXCHG and external state checks prevent ambiguous replay |
| Duplicate or stale transition calls cannot skip phases | PASS | Each transition has one exact predecessor |
| Sync/dirsync/readback interruption fails closed | PASS | No Persistence grant before the full continuation completes |
| Cleanup cannot become an operational bypass | PASS | Cleanup does not open creation or send gates |
| L0/L1 kill, close, restart, and recovery paths remain representable | PASS | Complete six-channel mapping preserved |
| Completion implies implementation authorization | NO | Separate governance authorization remains required |

## 13. Findings

### BLOCKER

None.

### HIGH

None.

### MEDIUM

None.

### LOW

None.

No advisory observation was promoted into a finding because no identified condition violated an operative requirement, made the Linux enforcement mapping non-executable, left a failure path undefined, weakened an older closure, or created a pre-release operational path.

## 14. Scope and mutation attestation

This rereview was confined to the canonical repository:

```text
/home/benja/projects/sniper-bot
```

The review target was exclusively:

```text
docs/LIVE_DESIGN_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPEC.md
```

The only review-produced repository mutation authorized for this task is this review record:

```text
docs/review/PRE_IU4_ENFORCED_PAPER_ACTIVE_RUNTIME_INTEGRATION_SPECIFICATION_REVISION_21_INDEPENDENT_READONLY_REREVIEW_2026-08-19.md
```

No change was made to:

- the target specification,
- the controlling resolution,
- Runtime documents or implementation,
- R3 material,
- State material,
- Workstation material,
- Scheduler material,
- Research material,
- Exchange material,
- Live material,
- any earlier review or resolution record.

No write-capable test was run.

No file was staged or committed.

No fetch or push was performed.

`scripts/build_rcc002_spec_bundle.py` was neither read, executed, nor changed.

`scripts/state_research` remained closed.

No S45 action was performed.

Pre-existing untracked artifacts were left untouched.

The review record’s own SHA-256 and line count must be computed and reported after its final serialization; embedding its own final hash in its contents would change that hash.

## 15. Exact next governance step

Because the verdict is `READY`, the next step is not direct implementation and not any exchange/live action.

The exact next governance sequence is:

1. perform the terminal R3 handoff for this exact Revision 21 specification identity;
2. run the frozen postrun validator exactly once against the terminal artifact;
3. require final R3 `PASS`;
4. bind the final code, input, profile, evidence, specification, and validator identities in the controlling final attestation;
5. only after that binding, issue a separate explicit file-exact mandate for **I1 Characterization / Pure Control Extraction**.

The following are not authorized by this record:

- skipping the terminal R3 handoff,
- rerunning or substituting the frozen validator outside its governed one-shot use,
- treating this rereview as the final R3 attestation,
- starting I1 without a separate file-exact mandate,
- advancing directly to I2 or a later implementation phase,
- activating exchange connectivity,
- activating live trading,
- altering L0/L1, PEE, ownership, Runtime, State, Scheduler, Research, Exchange, or Live authority.

## 16. Final verdict

```text
REVISION:21
TARGET_SHA256:ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0
TARGET_LINES:4605
BLOCKER:0
HIGH:0
MEDIUM:0
LOW:0
V20_H1:CLOSED
PRESERVATION:PASS
COMPLETION:PASS
SPECIFICATION_IMPLEMENTATION_READY:YES
IMPLEMENTATION_AUTHORIZED:NO
R3_FINAL_ATTESTATION_BOUND:NO
VERDICT:READY
```

Revision 21 is ready for the stated terminal governance handoff. It is not, by this record alone, authorized for implementation or operation.
