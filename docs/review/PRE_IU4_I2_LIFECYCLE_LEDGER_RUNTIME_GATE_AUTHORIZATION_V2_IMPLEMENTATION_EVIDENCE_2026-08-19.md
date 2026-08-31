# Pre-IU4 I2 Lifecycle Ledger / Runtime Gate / Authorization V2 — Implementation Evidence — 2026-08-19

## 1. Result

```text
IMPLEMENTATION_PACKAGE:I2_ONLY
I2_RESULT:PASS
FOUNDATION_IMPLEMENTATION_RESULT:PASS
TERMINAL_LEASE_CAPABILITY_V14_RESULT:PASS
ENFORCED_LOOP_ENTERED:NO
ADAPTER_V2_INVOKED:NO
ATOMIC_V2_CREATED:NO
EXCHANGE_OR_LIVE_MUTATION:NO
```

I2 implementation is complete.  Independent acceptance review has not been
started, and I3 has not been entered.  The final host-closure and authorizing
evidence is recorded in Section 12.  The
Python control-plane foundation, native ABI/build, real BPF verifier and real
six-hook LSM autoattach pass.  This continuation additionally passes real
Seccomp listener handoff, cross-process memfd, self-death, close-FSM,
six-channel `SO_PASSRIGHTS`, enabled private-Cgroup Guard, all four ordered
PIDFD/Liveness outcomes, the finite six-phase Close-transport classifier,
real Close-socket faults, TSYNC whole-TGID enforcement, Seccomp Stop
boundaries, final role filters, Guard-negative calls and bounded resource/
deadline measurements at the mandated counts.  It now also passes negative
listener-handoff PIDFD/source-FD/flags/ACK probes, Multi-CMSG `SCM_RIGHTS`
limits and an external `pidfd_getfd` baseline-versus-active-Guard comparison.
Implementation Continuation 2 additionally passes a real missing-ACK absolute
deadline with PIDFD kill, six root-invariant sibling-Broker Yama/Ptracer/
Dumpable/revocation scenarios, the complete finite shutdown
role/current-or-foreign-session-cookie/how/phase cross-product, and PIDFD/HUP,
missing-ACK and four-stage PIDFD-fallback probes inside one simultaneous
CPU/memory/FD/I/O resource envelope.
Implementation Continuation 3 additionally passes the kernel-real six-phase
by three receiver-lifecycle by three `SCM_RIGHTS`-variant matrix, including
mandatory `EPERM` after receiver crash and after `RELEASED`; the six-phase
socket-acquisition matrix over `pidfd_getfd` and `/proc/<pid>/fd`; and a fresh
full Capability-V14 plus resource/deadline run at 10,000 trials and 32 probes.
Implementation Continuation 4 additionally passes thirteen kernel-real
Listener-Handoff identity/FD/holder/revocation scenarios and a six-channel,
twelve-endpoint Guard matrix over owner TID, socket cookie, session nonce,
seal state, pre-/post-Release send state and ancillary control.  The BPF tag
now binds Cgroup, session, actual kernel socket cookie and owner TGID/TID; a
fixed compiler random seed makes three independent BTF-bearing objects
byteidentical.
Implementation Continuation 5 additionally closes the bounded Listener-ACK
writer and participant-stop/crash boundaries, binds runtime tags to exact
process starttime and SEND/RECEIVE direction, rejects partial TSYNC coverage,
and proves sender-close/-crash reference teardown.  The kernel-real matrix
adds 128 ACK-writer probes, 192 participant-boundary probes, 384 wrong-
starttime seals, 192 wrong-starttime and 192 wrong-direction sends, 192
prequeue Rights rejections across sender close/crash, 64 byteidentical
receiver inventories and 64 final socket/tag lifetime releases.  The bounded
resource/deadline envelope and the complete Live-L1/regression suites were
rerun after these changes.
Implementation Continuation 6 additionally characterizes the idle listener
without synthetic errno claims: 32 O_NONBLOCK `NOTIF_RECV` calls remain
blocked and require PIDFD termination, while 32 ptrace-interrupted blocked
calls expose kernel `-ERESTARTSYS`; this kernel does not deliver idle
Userspace `EAGAIN` or `EINTR`.  It also passes a six-channel Hidden-Endpoint/
TID matrix with 384 local duplicate detections, 768 blocked transfers, 384
synchronized wrong-TID races and 768 empty-queue snapshots.  Finally all six
current native 10,000-trial scenarios plus the 10,000-trial Python runtime-
channel scenario execute inside the simultaneous 90%-memory/FD/CPU/I/O
resource envelope.  This closes the currently implemented 10,000-trial
resource cross-product, but is not a claim that absent Revision-21 scenarios
were executed.
Implementation Continuation 7 additionally proves both post-TSYNC TID cases:
four TIDs created after Rights-Freeze inherit the kill filter in each of 32
probes, while `clone` and `clone3` are each killed by the final TSYNC basis
filter.  Across all six runtime channels it rejects 768 queued-packet races
in the mandatory post-filter snapshot, destroys all 768 disposable socket
pairs and queued references, and completes nine LSM-Seal/Rights-Freeze/final-
filter/durable-OPEN/Release boundary orderings with 192 results per ordering.
Governance for Continuation 8 resolves the idle-listener ambiguity from the
exact Revision-21 wording: idle `NOTIF_RECV` blocks until a notification or
fatal termination; readiness is mandatory before receive; idle O_NONBLOCK
`EAGAIN` and an idle Userspace-`EINTR` return are not separate capability
requirements.  Every errno actually returned after readiness remains totally
classified.  No synthetic errno or alternative kernel is claimed.
Implementation Continuation 8 additionally passes both deterministic
Trip/Renewal linearization orders at 10,000 trials, nine forbidden
Liveness-writer syscall filters at 32 probes each, exact PIDFD target/starttime
and `pidfd_send_signal` scalar matrices, and the complete memfd create/seal/
mapper negative matrix.  Close transport now crosses six phases, both
Approval recipients and fourteen outcome classes.  The Persistence Worker
matrix rejects all 480 forbidden request/state pairs, accepts and idempotently
replays exactly 96 bound requests, rejects 96 conflicting replays, 128
binding/shape faults and 32 fenced requests.  The Parent Guardian matrix adds
32 PIDFD/starttime bindings, 64 monotone renewals, 32 backwards-clock
rejections, 32 stopped-child bindings and 32 post-death renewal rejections.
The Guard now proves exact three-map ABI, read-only `BPF_OBJ_GET`, allowed
lookups, denied normal and `BPF_F_LOCK` updates, denied mmap, real translated
`cmpxchg`, six-link baseline restoration, map-ID RCU release and private-bpffs
unmount.
The complete simultaneous Resource envelope now executes all eight current
10,000-trial families and all 21 current 32-probe families, including the
enabled BPF-LSM Guard, Worker and Guardian matrices.  It passes 120,000
endpoint and 120,000 denied-Rights checks at 92.5742% memory, 224/256 FDs,
14 CPU-load generators, active I/O blocker and PIDs limit 64.  The final
integrated run records PIDFD dispatch at most 133,501 ns and Liveness HUP at
most 41,680 ns against the 5-ms budget.
Implementation Continuation 9 adds a machine-evaluated, fail-closed
Revision-21 Terminal-Capability Coverage Ledger V1 directly to the Capability
JSON.  It contains 97 unique atomic clauses from Sections 7.8.2 and 21.7,
each with macro family, source clause, scenario, exact trial/probe contract,
absolute JSON Evidence Pointer, comparison and expected/actual value.  Against
the kernel-real audit JSON, 73 clauses pass and 24 are explicitly BLOCKED;
there are no absent or malformed pointers among the claimed PASS rows.  The
ledger fingerprint is
`4aad4c30e27be38841b98a49021e044e83752cbc0075e639238361e25bb881d6`.
Consequently all eight macro families remain BLOCKED and the requested
governance decision is serialized as `macro_removal_authorization=DENIED` with
reason `ONE_OR_MORE_REVISION21_CLAUSES_ARE_BLOCKED_OR_UNMAPPED`.  No macro was
removed and `full_revision21_saturation_claimed` remains false.
The complete finite Capability Profile V14 still does not pass because the
eight historical end-to-end macro families remain explicitly listed by the
serializer and `full_revision21_saturation_claimed` remains false.  Every
concrete CONTINUATION-8 result actually executed is PASS, but this
implementation continuation does not silently promote the safety-relevant
authorization gate from BLOCKED to PASS.

That Continuation-9 state is historical.  Continuation 10 subsequently closed
all 24 then-blocked atomic clauses, obtained a `97/97 PASS` governance
preflight, removed the eight serialized Missing entries, reran the complete
mandatory and Resource matrix, and returned `CAPABILITY_V14:PASS` with
`full_revision21_saturation_claimed:true` as detailed in Section 12.

## 2. Controlling identities

```text
CANONICAL_REPOSITORY:/home/benja/projects/sniper-bot
HEAD:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
MAIN:c7ce0452aa2ccbf08c462784d68fa07b3dfe9595
ORIGIN_MAIN:89e13fecd1ab549ca7099818b1c9ad4984cb6f7a
MAIN_DIVERGENCE_BEHIND_AHEAD:0/6
MANDATE_SHA256:bbf2968cfc1de02edb54e1c6ed47951818f7fd6840b10b5d0b7c6ef652eb0517
REVISION_21_SHA256:ab8f80720a1d8fe49b9085bce63658bcaecf7f0a3ea70fb555559223090824e0
I1_READY_REREVIEW_2_SHA256:adc13abbec3a0458d712df729c2732bce8897be7ecf991a312839616e9687804
```

## 3. Workstation prerequisite remediation

The separately authorized prerequisite remediation performed:

- creation of `C:\Users\benja\.wslconfig`, SHA-256
  `958fbee36cc4e7dccb8a2565066880d013ffc0d10c3f6382fbaed4f36d913d58`;
- boot command line activation of
  `lsm=landlock,lockdown,yama,loadpin,safesetid,integrity,selinux,apparmor,tomoyo,bpf`;
- installation/verification of Clang/LLVM 21, bpftool 7.7, libbpf 1.6,
  libelf, zlib, make and pkg-config;
- complete WSL reboot, new boot ID
  `9ed1d0f6-4865-45c2-b35e-7eb940ca04b2`;
- active LSM list `capability,landlock,yama,safesetid,selinux,bpf,ima`;
- Linux `6.18.33.2-microsoft-standard-WSL2`, Yama `1`, BTF readable,
  `CONFIG_BPF_LSM=y`, `CONFIG_SECURITY_NETWORK=y`, and all six required
  BTF hook identities present.

## 4. Implemented identities

| Path | SHA-256 | Lines |
| --- | --- | ---: |
| `live_l1/core/paper_iu4_startup_gate.py` | `c4a1854f3b200525568a40205b39e9ce2e14c342bb860569ba7fcfe5e9c063cd` | 919 |
| `live_l1/core/paper_iu4_shadow_runtime_gate.py` | `98d986f3ac2e463b371998604d92b29aa113a507dd0f84bcbd3ff36a52efaf59` | 438 |
| `live_l1/core/paper_iu4_runtime_gate.py` | `447573e484bc13023a118ae61bf7615657293be629c30729748e64f0af7af7c5` | 201 |
| `live_l1/core/terminal_runtime_protocol.py` | `43ee7c763dd34b12ae82397aea5973925fe74f0b155281d7a4d175c84a120427` | 310 |
| `live_l1/core/terminal_parent_guardian.py` | `3f7fd22413fbeab2753def67a6d6068f85541dcad297b4449ae092465d9e218c` | 153 |
| `live_l1/core/terminal_persistence_worker.py` | `bc574df843266c772afad46fedd94948156a9c1e55f0690d3ec9abeea2e4a65d` | 123 |
| `live_l1/state/iu4_lifecycle_ledger.py` | `d72134195f66b1d39c09a2ca6b9919d8a9acf17c4490ab52d9abc2aebcd71337` | 438 |
| `live_l1/native/terminal_lease_protocol_v14.h` | `8872bd02879f566f7e8226d0d484bd4b79d85993df888968f255d20b05296551` | 26 |
| `live_l1/native/terminal_native_trip_broker.c` | `8e67b1c28f5975abf1f9a228de75ad859f183c51b9f30475ffb419cfea2f3bad` | 16 |
| `live_l1/native/terminal_kernel_lease_shim.c` | `21c615a08b5df5a7ac00eaa5ed59d6e2c8c062b2ee3990c0031ee587078e7794` | 6 |
| `live_l1/native/terminal_handoff_revocation_attestor.c` | `deecb86860f4a237717e10480e1e01e17c4ed5a01673e6dc8ae41740753cf41f` | 6 |
| `live_l1/native/terminal_runtime_socket_lsm_guard.bpf.c` | `116342f672a3286a8b55b1ba870c0ad5b8dcb9bbc723f9027ebe9a87bb94ac40` | 35 |
| `live_l1/native/terminal_lease_fault_fixture.c` | `49b6b29de8e22abe663ff3a400e5fc1f01276bd8d65ff45d0d73e192f79e497c` | 1,819 |
| `live_l1/tools/validate_terminal_lease_capability.py` | `b503466096d5fcd5b5a182c3c15ddb6790d718c2e1c88a18b8c462846ed93d14` | 4,245 |
| `live_l1/tools/terminal_lease_side_effect_observer.py` | `40844b2923661ba95852b202380e6c8cfc9b4c938e8e7203d3427e45af1a15ac` | 86 |
| `tests/live_l1/test_iu4_lifecycle_ledger.py` | `f01c2eda7ceec56fad18acec20a09afaa187b4fd4850ab17a974e6bfe8200093` | 50 |
| `tests/live_l1/test_paper_iu4_runtime_gate.py` | `c1137ddcdec7f40ccf463cfc28719d92ea4d766b5be81e6129f6e7bd174f500d` | 24 |
| `tests/live_l1/test_terminal_parent_guardian.py` | `db4c7eca376ea944a0aabd8187f5882f304c033016b28223420156e30b9eaad2` | 17 |
| `tests/live_l1/test_terminal_persistence_worker.py` | `4d1a24431f293a445f030c0bec97776ac0b3b2e2c71cf4e5b539d942e0de6392` | 25 |
| `tests/live_l1/test_terminal_lease_capability.py` | `992ec805539a5eadd1bfb20c60f4d9b3ce38469ef7b916919bbd67bd51779db9` | 123 |

No generated object, native binary, `vmlinux.h`, BPF pin or map was added to
the repository.

## 5. Implemented foundation

- strict Activation Authorization V2 and Restart/Recovery Authorization V1
  canonical records;
- explicit absolute external authorization loader with no search/fallback,
  symlink rejection, ownership/mode checks, forbidden-root exclusion and
  independent trust-anchor comparison;
- create-new, file/directory-fsynced, readback-verified Lifecycle Ledger V1;
- separate ledger tip, authority commit anchor and generation views;
- self-reference-free generation derivation, PREPARE/COMMIT validation,
  one-time restart authorization consumption and runtime close classification;
- sole mode-neutral OFF/SHADOW/ENFORCED classification with unchanged
  OFF/SHADOW facade behavior and deterministic I2 ENFORCED non-entry;
- pure protocol records, Control Word V3 encoding and finite transition sets;
- test-owned Parent Guardian and session/fencing-bound idempotent Persistence
  Worker foundation;
- native ABI assertions, lock-free CAS fixture, sealed memfd probe,
  `CLOCK_BOOTTIME` timer probe and disjoint attestor binary;
- a default-disabled BPF-LSM object containing and real-autoattaching exactly
  `socket_post_create`, `unix_stream_connect`, `socket_setsockopt`,
  `socket_sendmsg`, `socket_shutdown` and `file_receive`;
- external FD/FDINFO/`scm_fds`/lock inventory observer.

The continuation adds the following kernel-executed foundations:

- `SECCOMP_FILTER_FLAG_NEW_LISTENER | WAIT_KILLABLE_RECV`, parent
  `pidfd_open`/`pidfd_getfd`, listener ACK, source-FD close, Ptrace/Dumpable
  revocation, notification-ID validation and `EPERM` response; the ACK is a
  real `EFD_CLOEXEC` eventfd boundary;
- a cross-process `MFD_CLOEXEC | MFD_ALLOW_SEALING` Control Word mapping with
  exactly one surviving RW shared mapping, RO observer mapping,
  `F_SEAL_GROW|SHRINK|FUTURE_WRITE|SEAL` and rejected new RW mapping;
- six real abstract-AF_UNIX `SOCK_SEQPACKET` `connect`/`accept` channels per
  trial, twelve `SO_PEERCRED`/`SO_PASSRIGHTS=0` endpoint checks and two denied
  pre-queue Rights sends per channel;
- `SCM_MAX_FD`, stopped and crash-terminated pre-`recvmsg` receivers,
  persistent `scm_fds: 0`, empty queues and NULL/0-control `MSG_CTRUNC`
  autoclose checks;
- 32 Multi-CMSG probes containing two `SCM_RIGHTS` control messages with
  126 plus 127 FDs; every send is rejected with `EPERM` before queue entry;
- real `CLOCK_BOOTTIME` absolute-SIGKILL expiry while the target is
  `SIGSTOP`ped;
- four separately repeated kernel outcomes for successful Self-PIDFD
  `SIGKILL`, Self-error then Guardian-PIDFD `SIGKILL`, Self-/Guardian-error
  then Broker-PIDFD `SIGKILL`, and three PIDFD errors followed by exactly one
  Liveness-writer close with read-side EOF/HUP;
- six close-message phases crossed with fourteen transport outcome classes,
  preserving byteidentical retry payload/deadline and separating pre-CLOSED,
  post-CLOSED, COMMITTED-convergence, identical-duplicate and conflict
  classifications;
- six phases times 32 real `SOCK_SEQPACKET` probes for receive/queue-full
  `EAGAIN`, Short/invalid, `MSG_TRUNC`, peer HUP/error, timeout, lost delivery,
  byteidentical duplicates and conflicting duplicates;
- four preexisting worker TIDs per disposable TGID followed by a real
  `SECCOMP_FILTER_FLAG_TSYNC` Rights-freeze filter; the forbidden
  `setsockopt` rotates across worker TIDs and every one of 32 attempts ends the
  whole TGID with kernel `SIGSYS`;
- a complementary 32-probe post-TSYNC series creates four new TIDs only after
  installing the Rights-Freeze filter and rotates the forbidden `setsockopt`
  across them; every new TID inherits the filter and the whole TGID receives
  `SIGSYS`.  Separate final-basis probes reject both `clone` and `clone3` with
  `SECCOMP_RET_KILL_PROCESS`, 32/32 per syscall;
- Seccomp Notification stop boundaries before and after `NOTIF_RECV`:
  pre-Receive `SIGSTOP` yields terminal `ENOENT` and Broker PIDFD kill, while
  post-Receive `SIGSTOP` remains pending under `WAIT_KILLABLE_RECV`, the ID
  remains valid and Broker PIDFD kill is the terminal action;
- terminal classification of listener `ENOENT`, `EINTR`, `EAGAIN` and unknown
  errors; only `ENOENT` is claimed as kernel-real because an idle listener did
  not provide a safely reproducible artificial `NOTIF_RECV` EINTR/EAGAIN on
  this kernel;
- 26 final-role syscall filters, each repeated 32 times in a fresh TGID,
  spanning task/files-table creation, FD creation/duplication, socket creation,
  connect/accept, transfer, signal-policy and mapping/userfaultfd operations;
  every attempt ends as whole-TGID kernel `SIGSYS`;
- seven wrong-how/premature/duplicate/backward Guard transitions and twelve
  foreign-role shutdown attempts; all return `EPERM` and preserve the frozen
  `RELEASED` phase word;
- 32 negative listener handoffs covering invalid PIDFD `EBADF`, invalid source
  FD `EBADF`, nonzero `pidfd_getfd` flags `EINVAL` and explicit rejection of a
  wrong eventfd ACK;
- 32 missing-ACK handoffs that remain blocked through a 25-ms absolute
  `CLOCK_BOOTTIME` deadline and then terminate through exactly one Broker
  PIDFD `SIGKILL` inside the 100-ms fail-stop bound;
- six sibling-Broker handoff-policy scenarios, each repeated 32 times, covering
  correct Ptracer plus completed revocation, missing and wrong Ptracer,
  pre-acquisition `Dumpable=0`, failed `PR_SET_PTRACER=0` and failed
  `PR_SET_DUMPABLE=0`; every negative path ends in PIDFD kill.  Root trials
  normalize only the test children to equal real/effective/saved credentials
  and empty capability sets before exercising Yama;
- seven additional sibling-Broker boundary scenarios, each repeated 32 times:
  mismatched real credentials, a wrong non-listener source FD, source close
  before acquisition, target `SIGSTOP` and target crash before acquisition,
  a second `pidfd_getfd`, and a second listener holder.  Together with the
  existing six cases this is 416/416 PASS; the positive path also verifies
  the exact reserved Broker target FD and exact `anon_inode:seccomp notify`
  identity;
- 32 paired external-acquisition probes: with the same target Parent FD and
  explicit Yama `PR_SET_PTRACER`, the out-of-Cgroup baseline `pidfd_getfd`
  succeeds while the caller moved into the active Guard Cgroup is rejected by
  `file_receive` with `EPERM`; the frozen `RELEASED` phase remains unchanged;
- the enabled Guard probe now starts at `LISTENER_HANDOFF`, uses a real
  external `pidfd_getfd` to drive `file_receive` atomically to
  `LISTENER_RECEIVED`, then drives Attestor revocation and Guard bootstrap via
  `socket_shutdown` hooks before creating/tagging the runtime sockets; all
  five phases through `RELEASED` are therefore hook-driven while config and
  phase maps are frozen;
- 32 repetitions of the complete shutdown cross-product over three roles,
  three current-session and three foreign-session Control-Socket cookies,
  three `shutdown` values and six phases: 10,240 negative calls return
  `EPERM` without mutation and 128 exact positive calls return `EINPROGRESS`
  after hook-only CMPXCHG;
- a Guard-attached phase/receiver-lifecycle/SCM cross-product over all six
  phases, `READY_ALIVE`, `STOPPED_BEFORE_RECVMSG` and
  `CRASHED_BEFORE_SEND`, and one FD, `SCM_MAX_FD=253`, and two CMSGs with
  126 plus 127 FDs.  All 1,728 sends return `EPERM`, including after
  `RELEASED` and with no surviving receiver; 384 live/stopped snapshots show
  an empty queue and `scm_fds: 0`, and all 576 phase checks are unchanged;
- a Guard-attached socket-acquisition cross-product over all six phases and 32
  probes per phase.  All 192 `pidfd_getfd` attempts return `EPERM`, all 192
  `/proc/<pid>/fd` socket opens return `ENXIO`, and all 192 phase checks remain
  unchanged.  `file_receive` now distinguishes socket files from the
  non-socket listener-handoff surrogate, and post-`RELEASED` `socket_sendmsg`
  permits control-free traffic but rejects nonempty ancillary control;
- a six-channel/twelve-endpoint Guard cross-product repeated 32 times.  It
  rejects 3,456 foreign-session, foreign-TID, foreign-cookie, duplicate-seal,
  pre-Release and ancillary-control operations with `EPERM`; accepts 384
  exact owner/session/cookie-bound control-free send/receive operations after
  `RELEASED`; proves 768 empty queues with `scm_fds: 0`; and preserves the
  phase word in 160 checks.  Accepted peer sockets receive their own kernel
  cookie rather than inheriting the connector cookie;
- 32 probes over six real abstract `listen/connect/accept` channels bind the
  connector to SEND and the accepted peer to RECEIVE and bind both to the
  exact `/proc/<pid>/stat` starttime represented from BPF task boottime.  The
  extended matrix rejects 384 wrong-starttime seals, 192 wrong-starttime
  sends and 192 wrong-direction sends with `EPERM`; all 224 phase checks are
  unchanged.  A separate 32-probe partial-TSYNC fixture proves that a
  thread-local filter leaves one of four pre-existing worker TIDs able to call
  `setsockopt`, detects that gap and blocks OPEN rather than accepting partial
  coverage;
- 32 probes per `SENDER_CLOSE` and `SENDER_SIGKILL_CRASH` execute one-FD,
  `SCM_MAX_FD=253` and split 126+127-FD CMSG variants after `RELEASED`.  All
  192 sends return exact prequeue `EPERM`; 64 receiver snapshots retain
  byteidentical Queue/`scm_fds: 0`/FD/FDINFO/OFD/Lock identity; all 64 socket
  inodes and their attached SK-storage tag lifetimes disappear after final
  teardown without phase mutation;
- 32 idle-listener probes prove that `SECCOMP_IOCTL_NOTIF_RECV` remains
  blocked even with `O_NONBLOCK`; this kernel does not supply idle EAGAIN.
  A second 32-probe series stops the already blocked ioctl under ptrace and
  observes exact register return `-ERESTARTSYS`; it does not claim a
  Userspace-EINTR return.  Both unavailable errno paths remain terminally
  classified fail closed;
- a disposable six-channel Hidden-Endpoint/TID matrix repeated 32 times
  detects 384 local duplicate references, rejects 192 endpoint transfers in
  each of four pre-/post-Release carrier/tag variants, proves 768 empty
  queues, and rejects 192 synchronized Close-vs-Wrong-TID plus 192 migrated-
  duplicate Wrong-TID `setsockopt` races with unchanged phases;
- four real queued-packet variants per each of six channels and 32 probes:
  control-free and one-FD Rights packets queued either before the final
  snapshot or after a previously passed pre-filter snapshot.  The mandatory
  post-filter snapshot rejects all 768 cases, including 384 real
  `scm_fds: 1` Rights queues; all 768 socket pairs, queues and kernel-held
  references are destroyed, the userspace FD inventory returns exactly to
  baseline, and Same-Session retry remains forbidden;
- a Guard-attached nine-ordering channel matrix over all six directions and
  32 probes: Rights sends before/during/after the LSM seal, during/after the
  Rights-Freeze TSYNC, during/after the final sendmsg role filter, after
  durable OPEN before Release and after Release.  Every LSM path returns
  exact `EPERM`; a completed final filter produces whole-process `SIGSYS`.
  Each ordering passes 192/192, all 768 live queue snapshots remain empty
  with `scm_fds: 0`, and all 288 phase-word checks remain unchanged;
- the accepted idle governance semantics
  `BLOCKING_IDLE_UNTIL_NOTIFICATION_OR_FATAL_TERMINATION`: the Broker must
  establish readable/HUP/ERR readiness before `NOTIF_RECV`; idle nonblocking
  EAGAIN and idle Userspace EINTR are not required, while every actually
  returned receive errno remains fail-closed and totally classified;
- 10,000 trials per each of `RENEWAL_BEFORE_TRIP` and
  `TRIP_BEFORE_RENEWAL`; every post-Trip renewal fails and the terminal word
  remains immutable;
- 32 probes per each of `read`, `write`, `readv`, `writev`, `splice`,
  `vmsplice`, `tee`, `sendfile` and `epoll_ctl` against the sole Liveness
  writer.  The exact forbidden-syscall timestamp is shared atomically; under
  root validation a blocking FIFO/1 observer removes userspace scheduler
  dispatch from the fatal-filter-to-HUP interval, while all load generators
  continue at nice 19.  Every disposable TGID dies with `SIGSYS`, loses its
  last writer and exposes HUP/EOF within 5 ms;
- 32 probes over all eleven memfd create/seal/mapper faults, including missing
  `MFD_ALLOW_SEALING`, initial/incomplete/premature/forbidden seals, every
  forbidden writable role and a new writable map after
  `F_SEAL_FUTURE_WRITE`; all 352 negative cases are detected;
- 32 three-role PIDFD binding probes with exact `/proc/self/fdinfo` target,
  process starttime and signal-0 checks, 192 wrong-target, 96 wrong-starttime,
  96 invalid-flags, 96 non-null-siginfo and 96 stale-target rejections.  A
  separate Seccomp argument filter accepts only the exact bound PIDFD,
  `SIGKILL`, NULL siginfo and flags zero and kills every scalar variant;
- a Persistence Worker matrix over all three request types and six control
  states and a Parent Guardian matrix over test-owned child PIDFD/starttime,
  monotone and backwards `CLOCK_BOOTTIME`, child stop, PIDFD kill and dead-
  child renewal rejection, all repeated 32 times;
- exact Guard map ABI for `config_map`, `phase_map` and `socket_tags`; two
  real `BPF_OBJ_GET|BPF_F_RDONLY` descriptors permit lookup but reject normal
  and `BPF_F_LOCK` updates and mmap.  The loaded shutdown program contains a
  real translated `cmpxchg`; after every probe all six links return to the
  baseline, loaded map IDs disappear after bounded RCU observation and the
  private bpffs is unmounted;
- 32 PIDFD-dispatch and Liveness-HUP deadline measurements below 5 ms inside a
  simultaneous private resource Cgroup at 92.5994% memory utilization with
  69,529,600-byte reserve, FD `224/256`, 14 workload-bound CPU burners, a live
  I/O blocker, PIDs limit 64 and one-nanosecond `CLOCK_BOOTTIME` resolution.
  The same envelope executes all eight current 10,000-trial scenarios and all
  21 current 32-probe scenarios, including missing-ACK, four PIDFD fallbacks,
  BPF Guard, Worker and Guardian, plus 120,000 endpoint and 120,000 denied-
  Rights checks.  This is complete for every scenario currently represented
  by the validator, but the serializer does not claim the eight historical
  Revision-21 macro families complete;
- an enabled BPF-LSM Guard in a test-private Cgroup, PID-namespace-bound actor
  lookup via `bpf_get_ns_current_pid_tgid`, frozen config/phase maps, blocked
  userspace update, pre-Release `EPERM`, hook-only CMPXCHG to `RELEASED` and
  successful post-Release send.
- normalized BPF debug/file prefix maps and a fixed Clang random seed; final
  Continuation-8 validator and immediate fresh reproduction build
  produced the identical BPF object SHA-256
  `1081c9b650684f3ef16c3562c97b7eff0905bc95fcb7da814a46e2cd1b64a962`,
  so the profile identity no longer depends on its temporary output path.
- a 97-row Revision-21 Terminal-Capability Coverage Ledger whose evaluator
  rejects duplicate IDs, relative/missing JSON pointers, unknown comparison
  operators and every expected/actual mismatch.  Macro removal and the
  `full_revision21_saturation_claimed` transition are computed only when all
  rows PASS; an empty or partial evidence object deterministically blocks all
  97 rows and all eight macro families.

## 6. Verification results

```text
focused_startup:12/12_PASS
focused_lifecycle_ledger:5/5_PASS
focused_mode_neutral_gate:3/3_PASS
focused_shadow_runtime:10/10_PASS
focused_shadow_observation:18/18_PASS
focused_safe_launch:3/3_PASS
focused_guardian:1/1_PASS
focused_persistence_worker:2/2_PASS
focused_terminal_capability_contract:5/5_PASS
focused_total:59/59_PASS
full_tests_live_l1:373/373_PASS
full_tests_regression:170/170_PASS
py_compile:PASS
git_diff_check:PASS
native_compile_Werror:PASS
native_broker_lockfree_trials:10000/10000_PASS
native_control_word_trials:10000/10000_PASS
runtime_close_fsm_trials:10000/10000_PASS
runtime_close_transport_trials:10000/10000_PASS
runtime_close_transport_phase_probes:32/32_PER_PHASE_PASS
runtime_close_transport_phases:6/6_PASS
runtime_close_transport_outcome_classes:14/14_PASS
runtime_close_socket_faults:192/192_PER_CLASS_PASS
runtime_close_socket_fault_classes:9/9_PASS
seccomp_listener_handoff_trials:10000/10000_PASS
seccomp_listener_handoff_startup_probes:32/32_PASS
seccomp_handoff_invalid_pidfd_EBADF:32/32_PASS
seccomp_handoff_invalid_source_fd_EBADF:32/32_PASS
seccomp_handoff_invalid_flags_EINVAL:32/32_PASS
seccomp_handoff_wrong_ACK_rejected:32/32_PASS
seccomp_handoff_missing_ACK_deadline_pidfd_kill:32/32_PASS
seccomp_handoff_missing_ACK_deadline_ns:25000000_PASS
seccomp_handoff_missing_ACK_failstop_budget_ns:100000000_PASS
seccomp_handoff_sibling_policy_scenarios:13/13_PASS
seccomp_handoff_sibling_policy_probes:32/32_PER_SCENARIO_PASS
seccomp_handoff_root_credentials_normalized_and_caps_empty:PASS
seccomp_handoff_wrong_real_credentials_EPERM:32/32_PASS
seccomp_handoff_wrong_source_identity_rejected:32/32_PASS
seccomp_handoff_source_closed_EBADF:32/32_PASS
seccomp_handoff_target_stopped_pidfd_kill:32/32_PASS
seccomp_handoff_target_crashed_ESRCH:32/32_PASS
seccomp_handoff_second_pidfd_getfd_EPERM:32/32_PASS
seccomp_handoff_second_listener_holder_pidfd_kill:32/32_PASS
seccomp_handoff_ack_writer_scenarios:4/4_PASS
seccomp_handoff_ack_writer_probes:32/32_PER_SCENARIO_PASS
seccomp_handoff_participant_boundary_scenarios:6/6_PASS
seccomp_handoff_participant_boundary_probes:32/32_PER_SCENARIO_PASS
seccomp_handoff_reserved_broker_target_fd_exact:PASS
seccomp_handoff_listener_anon_inode_identity_exact:PASS
seccomp_stop_boundary_probes:32/32_PASS
seccomp_pre_receive_ENOENT_terminal_kill:PASS
seccomp_post_receive_SIGSTOP_pending_pidfd_kill:PASS
listener_terminal_classification_probes:32/32_PASS
listener_real_ENOENT:PASS
listener_synthetic_idle_EINTR_EAGAIN_kernel_claim:NO
listener_idle_nonblock_NOTIF_RECV_observed_blocking:32/32_PASS
listener_idle_nonblock_EAGAIN_supported:NO
listener_idle_interrupt_kernel_ERESTARTSYS:32/32_PASS
listener_idle_userspace_EINTR_claim:NO
listener_governance_semantics:BLOCKING_IDLE_UNTIL_NOTIFICATION_OR_FATAL_TERMINATION
listener_readiness_before_NOTIF_RECV:REQUIRED
listener_idle_EAGAIN_requirement:NO
listener_idle_userspace_EINTR_requirement:NO
cross_process_memfd_trials:10000/10000_PASS
cross_process_memfd_startup_probes:32/32_PASS
memfd_negative_scenarios:11/11_PASS
memfd_negative_detections:352/352_PASS
trip_renewal_RENEWAL_BEFORE_TRIP_trials:10000/10000_PASS
trip_renewal_TRIP_BEFORE_RENEWAL_trials:10000/10000_PASS
liveness_writer_blocked_syscalls:9/9_PASS
liveness_writer_filter_probes:32/32_PER_SYSCALL_PASS
liveness_writer_whole_tgid_SIGSYS_HUP_EOF:PASS
selfdeath_stopped_target_probes:32/32_PASS
pidfd_self_success_probes:32/32_PASS
pidfd_guardian_fallback_probes:32/32_PASS
pidfd_broker_fallback_probes:32/32_PASS
pidfd_all_error_liveness_hup_probes:32/32_PASS
pidfd_binding_roles:3/3_PASS
pidfd_binding_startup_probes:32/32_PASS
pidfd_scalar_filter_negative_scenarios:5/5_PASS
pidfd_scalar_filter_probes:32/32_PER_SCENARIO_PASS
tsync_role_filter_probes:32/32_PASS
tsync_preexisting_worker_tids:4/4_PER_PROBE_PASS
tsync_forbidden_setsockopt_whole_tgid_SIGSYS:PASS
partial_tsync_detection_probes:32/32_PASS
partial_tsync_OPEN_blocked:PASS
post_tsync_new_TIDs:4/4_PER_PROBE_PASS
post_tsync_new_TID_inherited_setsockopt_SIGSYS:32/32_PASS
post_tsync_final_clone_KILL_PROCESS:32/32_PASS
post_tsync_final_clone3_KILL_PROCESS:32/32_PASS
final_role_filter_syscalls:26/26_PASS
final_role_filter_probes:32/32_PER_SYSCALL_PASS
final_role_filter_whole_tgid_SIGSYS:PASS
runtime_channel_trials:10000/10000_PASS
runtime_channel_endpoint_checks:120000/120000_PASS
runtime_channel_denied_rights_sends:120000/120000_PASS
scm_max_fd_probes:32/32_PASS
multi_cmsg_126_plus_127_fd_probes:32/32_PASS
stopped_or_crashed_receiver_probes:32/32_PASS
null_control_autoclose_probes:32/32_PASS
prefilter_empty_snapshots_before_race:384/384_PASS
postfilter_queued_packet_rejections:768/768_PASS
postfilter_plain_queue_rejections:384/384_PASS
postfilter_scm_rights_queue_rejections:384/384_PASS
postfilter_socket_queue_reference_teardowns:768/768_PASS
postfilter_same_session_retry_allowed:NO
enabled_private_cgroup_guard_probe:PASS
config_and_phase_map_freeze:PASS
userspace_phase_update_blocked:PASS
hook_file_receive_LISTENER_HANDOFF_to_LISTENER_RECEIVED:PASS
hook_attestor_LISTENER_RECEIVED_to_HANDOFF_REVOKED_GRANTED:PASS
hook_guard_HANDOFF_REVOKED_GRANTED_to_BOOTSTRAP:PASS
hook_only_final_phase_RELEASED:PASS
guard_wrong_how_premature_duplicate_backward:7/7_PASS
guard_foreign_role_attempts:12/12_PASS
guard_negative_phase_word_unchanged:PASS
guard_shutdown_roles:3/3_PASS
guard_shutdown_current_session_cookies:3/3_PASS
guard_shutdown_foreign_session_cookies:3/3_PASS
guard_shutdown_how_values:3/3_PASS
guard_shutdown_phases:6/6_PASS
guard_shutdown_cross_product_denials:10240/10240_PASS
guard_shutdown_authorized_cmpxchg:128/128_PASS
external_pidfd_getfd_baseline_successes:32/32_PASS
external_pidfd_getfd_guarded_EPERM:32/32_PASS
external_pidfd_getfd_phase_word_unchanged:PASS
guard_scm_phase_receiver_lifecycle_phases:6/6_PASS
guard_scm_receiver_lifecycles:3/3_PASS
guard_scm_variants:3/3_PASS
guard_scm_EPERM:1728/1728_PASS
guard_scm_empty_queue_zero_scm_fds:384/384_PASS
guard_scm_phase_word_unchanged:576/576_PASS
guard_socket_acquisition_phases:6/6_PASS
guard_socket_pidfd_getfd_EPERM:192/192_PASS
guard_socket_proc_fd_ENXIO:192/192_PASS
guard_socket_acquisition_phase_word_unchanged:192/192_PASS
runtime_guard_channels_endpoints:6/12_PASS
runtime_guard_foreign_session_setsockopt_EPERM:384/384_PASS
runtime_guard_foreign_tid_setsockopt_EPERM:384/384_PASS
runtime_guard_duplicate_setsockopt_EPERM:384/384_PASS
runtime_guard_foreign_cookie_setsockopt_EPERM:384/384_PASS
runtime_guard_pre_release_send_EPERM:384/384_PASS
runtime_guard_foreign_session_send_EPERM:384/384_PASS
runtime_guard_foreign_tid_send_EPERM:384/384_PASS
runtime_guard_foreign_cookie_send_EPERM:384/384_PASS
runtime_guard_ancillary_send_EPERM:384/384_PASS
runtime_guard_released_owner_send_receive:384/384_PASS
runtime_guard_empty_queue_zero_scm_fds:768/768_PASS
runtime_guard_phase_word_unchanged:288/288_PASS
runtime_guard_wrong_starttime_setsockopt_EPERM:384/384_PASS
runtime_guard_wrong_starttime_send_EPERM:192/192_PASS
runtime_guard_wrong_direction_send_EPERM:192/192_PASS
runtime_guard_channel_seal_filter_boundary_orderings:9/9_PASS
runtime_guard_rights_before_LSM_seal_EPERM:192/192_PASS
runtime_guard_rights_during_LSM_seal_EPERM:192/192_PASS
runtime_guard_rights_after_LSM_seal_before_freeze_EPERM:192/192_PASS
runtime_guard_rights_during_freeze_TSYNC_EPERM:192/192_PASS
runtime_guard_rights_after_freeze_before_final_filter_EPERM:192/192_PASS
runtime_guard_rights_during_final_filter_EPERM_or_SIGSYS:192/192_PASS
runtime_guard_rights_after_final_filter_SIGSYS:192/192_PASS
runtime_guard_rights_after_durable_OPEN_before_release_EPERM:192/192_PASS
runtime_guard_rights_after_release_EPERM:192/192_PASS
runtime_sender_close_crash_lifecycles:2/2_PASS
runtime_sender_teardown_prequeue_EPERM:192/192_PASS
runtime_sender_teardown_receiver_identity:64/64_PASS
runtime_sender_teardown_socket_tag_release:64/64_PASS
runtime_sender_teardown_phase_word_unchanged:64/64_PASS
runtime_hidden_local_dup_inventory:384/384_PASS
runtime_hidden_pre_release_carrier_transfer_EPERM:192/192_PASS
runtime_hidden_durable_pre_release_transfer_EPERM:192/192_PASS
runtime_hidden_released_untagged_transfer_EPERM:192/192_PASS
runtime_hidden_released_tagged_ancillary_EPERM:192/192_PASS
runtime_hidden_close_vs_wrong_tid_EPERM:192/192_PASS
runtime_hidden_migrated_dup_wrong_tid_EPERM:192/192_PASS
runtime_hidden_empty_queue_snapshots:768/768_PASS
runtime_hidden_phase_word_unchanged:160/160_PASS
persistence_worker_accepted_state_pairs:96/96_PASS
persistence_worker_rejected_state_pairs:480/480_PASS
persistence_worker_idempotent_replays:96/96_PASS
persistence_worker_conflicting_replays_rejected:96/96_PASS
persistence_worker_binding_shape_rejections:128/128_PASS
persistence_worker_fenced_rejections:32/32_PASS
guardian_pidfd_starttime_bindings:32/32_PASS
guardian_clock_boottime_renewals:64/64_PASS
guardian_backward_clock_rejections:32/32_PASS
guardian_stopped_child_bindings:32/32_PASS
guardian_postdeath_renewal_rejections:32/32_PASS
guard_map_abi_exact:PASS
guard_readonly_obj_get_descriptors:2/2_PASS
guard_readonly_lookup:2/2_PASS
guard_readonly_normal_update_rejections:2/2_PASS
guard_readonly_BPF_F_LOCK_update_rejections:2/2_PASS
guard_non_mmapable_rejections:2/2_PASS
guard_phase_cmpxchg_translated:PASS
guard_link_baseline_restored:PASS
guard_map_RCU_release_observation_ns:43362304/2000000000_PASS
deadline_pidfd_dispatch_max_ns:133501/5000000_PASS
deadline_liveness_hup_max_ns:41680/5000000_PASS
resource_deadline_pidfd_dispatch_probes:32/32_PASS
resource_deadline_liveness_hup_probes:32/32_PASS
resource_missing_ACK_deadline_pidfd_kill_probes:32/32_PASS
resource_pidfd_fallback_scenarios:4/4_PASS
resource_pidfd_fallback_probes:32/32_PER_SCENARIO_PASS
resource_memory_utilization_ppm:925994_PASS
resource_memory_reserve_bytes:69529600_PASS
resource_fd_count_limit_headroom:224/256/32_PASS
resource_cpu_burners:14_PASS
resource_cpu_load_generator_nice:19_PASS
resource_io_blocker:PASS
resource_current_10000_trial_scenarios:8/8_PASS
resource_current_10000_trials_per_scenario:10000/10000_PASS
resource_current_startup_scenarios:21/21_PASS
resource_current_startup_probes_per_scenario:32/32_PASS
resource_runtime_channel_endpoint_checks:120000/120000_PASS
resource_runtime_channel_denied_rights_sends:120000/120000_PASS
revision21_coverage_clause_ids_unique:97/97_PASS
revision21_coverage_absolute_JSON_pointers:73/73_PASS
revision21_coverage_pass_clauses:73/97
revision21_coverage_blocked_clauses:24/97
revision21_coverage_absent_claimed_pointers:0_PASS
revision21_coverage_macro_families:0/8_PASS
revision21_coverage_macro_removal_authorization:DENIED
revision21_coverage_result:BLOCKED
bpf_verifier_six_programs:PASS
bpf_lsm_autoattach_six_links:PASS
temporary_bpf_link_cleanup:PASS
temporary_bpffs_unmount:PASS
bpf_reproducible_build_roots:2/2_IDENTICAL_PASS
```

The final fail-closed validator run used exactly:

```text
--certification-trials 10000
--startup-probes 32
CAPABILITY_V14:BLOCKED
FOUNDATION_RESULT:PASS
CANDIDATE_PROFILE_FINGERPRINT:83ad16c65476396c3b6b62ae6583982a1ff53bd4ed7e26fb34bb67bd462a7117
CAPABILITY_JSON_SHA256:5b35d6bfcc9d18d2c58e41635623cf642f7d107bf04532e7a369a679602c9451
CAPABILITY_OUTPUT_ROOT:/tmp/iu4-cap-v14-cont9-coverage-audit-20260819-1
BPF_OBJECT_SHA256:29709aeef230858a7e45c3b59f650344ac2d064f97a23f3112390fa9dbf6102f
REVISION21_COVERAGE_FINGERPRINT:4aad4c30e27be38841b98a49021e044e83752cbc0075e639238361e25bb881d6
REVISION21_COVERAGE_PASS_BLOCKED:73/24
REVISION21_MACRO_REMOVAL_AUTHORIZATION:DENIED
RESOURCE_CURRENT_10000_TRIAL_SCENARIOS:8/8_PASS
RESOURCE_CURRENT_32_PROBE_SCENARIOS:21/21_PASS
```

The earlier development serializer output that said `PASS` was rejected by
the implementation's own contract audit and was not used as final evidence.
The final serializer returns code `1` and `BLOCKED` until every mandatory
scenario family is implemented.

## 7. Open mandatory scenario families

```text
SECCOMP_NEW_LISTENER_WAIT_KILLABLE_PIDFD_GETFD_HANDOFF_AND_REVOCATION
SIX_RUNTIME_CHANNELS_TWELVE_ENDPOINTS_RIGHTS_FREEZE_AND_FINAL_ROLE_FILTERS
SO_PASSRIGHTS_EPERM_PREQUEUE_STOP_CRASH_SCM_MAX_FD_REFERENCE_CLEANUP
CONTROL_WORD_SINGLE_WRITER_CROSS_PROCESS_MEMFD_MAPPING_AND_SEAL_ATTESTATION
KERNEL_SELF_DEATH_LEASE_WHOLE_TGID_STOP_SUSPEND_AND_PIDFD_FALLBACK
RUNTIME_SESSION_CLOSE_PROTOCOL_V8_COMPLETE_FAULT_AND_DEADLINE_FSM
GUARD_CONFIG_ENABLE_PRIVATE_CGROUP_MAP_FREEZE_READONLY_FD_AND_PIN_LIFETIME
TEN_THOUSAND_TRIALS_AND_THIRTY_TWO_PROBES_PER_EACH_REQUIRED_SCENARIO
```

The one-to-one ledger resolves these macros into the following 24 blocking
atomic clauses:

```text
R21-TLH-012  all Yama modes other than ptrace_scope=1
R21-TLH-013  unexpected pidfd_getfd return-FD
R21-TLH-014  zero runtime-socket/sendmsg inventory on every handoff failure
R21-CHN-015  foreign and racing bootstrap connects
R21-CHN-016  independent SO_PASSCRED/controlbuffer endpoint attestation
R21-RGT-007  every SCM_RIGHTS FD count from one through SCM_MAX_FD
R21-MFD-010  external null pipe-page/temporary-writer inventory
R21-SDL-009  Guardian capability loss and Guardian/Broker/Shim stall/death matrix
R21-SDL-010  every blockable signal before/after receive and handler/unmask/SA_RESTART
R21-SDL-011  request-TID stop with healthy Broker and stalled Broker
R21-SDL-012  whole-child stop before and after notification
R21-SDL-013  suspend/resume self-death series
R21-CLS-007  orderly-close/renewal both linearization orders
R21-CLS-008  complete close errno/framing/identity/peer taxonomy
R21-CLS-009  complete Worker generation/peer/sequence/journal/state binding
R21-CLS-010  next-start Terminal-Gap-Recovery close boundary matrix
R21-GRD-011  map create/freeze/create-FD negative injection
R21-GRD-012  BPF program tags, pin inodes and private bpffs mount identity
R21-RES-010  FD limit minus 16 rather than minus 32
R21-RES-011  inherited FD saturation inside every exec scenario
R21-RES-012  reserved role CPUs and foreign runnable-task inventory
R21-RES-013  compiler/linker/libc/libatomic artifact hashes
R21-RES-014  mlockall/NUMA/hotplug/x32 envelope
R21-RES-015  complete external per-trial kernel timestamp manifest
```

These remain fail-closed end-to-end macro gaps, not accepted deferrals.  The
idle-semantics issue is no longer one of them: governance accepts blocking
idle receive and does not require idle O_NONBLOCK EAGAIN or idle Userspace
EINTR; readiness gating and total classification of any returned errno remain
mandatory.  Continuation 8 closes the requested Trip/Renewal, Liveness-writer,
PIDFD scalar/binding, memfd negative, Worker, Guardian and Guard map/link
adversaries, and the Resource envelope now executes every scenario currently
enumerated by the validator: 8 full-trial families and 21 startup families.

The serializer now emits the reviewable one-to-one Revision-21 clause ledger.
All 97 atomic rows name their source clause, concrete scenario, required probe
count, absolute JSON evidence pointer, comparison and observed value.  The
ledger proves 73 rows and identifies the 24 rows above as genuinely missing;
no row is credited without a resolvable evidence field.  Consequently all
eight historical macro families remain BLOCKED,
`full_revision21_saturation_claimed:false`, and governance records
`macro_removal_authorization:DENIED`.  The current run proves complete
saturation of the implemented finite 8-family/21-startup matrix, but correctly
does not equate that fact with complete Revision-21 authorization.  The
serializer returns code `1` and cannot authorize OPEN.

## 8. Preservation and side effects

All twelve Section-5 preservation hashes remain exact, including
`paper_iu4_adapter.py`, `paper_atomic_coordinator.py`, `loop.py`,
`paper_execution_control.py`, `execution.py` and the accepted I1 tests.
The pre-existing tracked I1 change in `execution.py` was not modified by I2.
Foreign untracked artifacts were not changed.  The excluded bundle script was
not read, executed, modified, staged or committed.

No real trading process, state, journal, scheduler, Exchange or Live path was
entered.  All native outputs, BPF pins/maps/links and write tests used unique
temporary roots.  Every Guard teardown restored the exact pre-run LSM-link
set; the final read-only inventory contained 18 pre-existing LSM links, which
were left unchanged.  Temporary bpffs mounts were removed.  Four empty Cgroup
directories created by failed Continuation-8 diagnostic runs were verified
`populated 0` and removed; foreign Resource-Cgroups were not changed.  No
Continuation-9 validator or fixture process remains; older foreign
Continuation-2 sandbox wrapper processes observed by the broad inventory were
also left unchanged.  The securityfs mount created only for the kernel-real
coverage-audit run was removed after the run.  No authorizing final run was
started because the governance prerequisite for macro removal failed.

## 9. Exact next step

I2 independent review and I3 remain prohibited.  The idle-listener governance
decision is complete.  The exact next workstream is:

```text
IU4-I2-LIFECYCLE-LEDGER-RUNTIME-GATE-AUTHORIZATION-V2-IMPLEMENTATION-CONTINUATION-10
```

That continuation must implement and kernel-real verify the 24 atomic BLOCKED
rows listed in Section 7.  It must then regenerate the ledger.  Only a 97/97
PASS ledger may governance-authorize removal of the eight historical macro
Missing entries, set `full_revision21_saturation_claimed:true`, and permit the
entire mandatory and Resource matrix to be rerun as the authorizing final run.
`I2_RESULT:PASS` remains forbidden until that final validator itself returns
zero.

## 10. Continuation 10 — atomic clause implementation and kernel observers

Continuation 10 implemented and kernel-real verified 21 of the 24 atomic
clauses that were BLOCKED at the Continuation-9 handoff.  The resulting
Revision-21 ledger is `94/97 PASS`; it deliberately remains `BLOCKED` and did
not remove any of the eight macro entries.

The final successful kernel-real run for this continuation used:

```text
CAPABILITY_OUTPUT_ROOT:/tmp/iu4-cap-v14-cont10-kernel-observers-20260819-2
CAPABILITY_V14:BLOCKED
FOUNDATION_RESULT:PASS
CANDIDATE_PROFILE_FINGERPRINT:85a5a491e80b78ccde052814d32b66e45652b30e3863874678dcb448fc20baa7
CAPABILITY_JSON_SHA256:19f92364da68e99202d20d53c65f0953a017930ac63c09eca46e60a6a19a8a09
REVISION21_COVERAGE_FINGERPRINT:b03cc314e777a802ffe9b1866e06ddc9ee636ed0860876e3996280ab82e6b6d9
REVISION21_COVERAGE_PASS_BLOCKED:94/3
REVISION21_MACRO_REMOVAL_AUTHORIZATION:DENIED
```

### 10.1 Kernel-real records added

The validator now rejects incomplete, duplicate or unexpected Native records
before serialization.  Direct and resource-saturated runs both proved:

```text
role_stall_and_capability_loss:160/160_PASS
blockable_signal_pending:3968/3968_PASS
signal_mutation_sigsys:320/320_PASS
request_tid_broker:64/64_PASS
handoff_failure_kernel_observer:608/608_PASS
liveness_pipe_kernel_observer:288/288_PASS
resource_exec_fd_inheritance:5961/5961_PASS
resource_exec_open_fds:240/256
```

The five-role matrix covers Guardian death through `PDEATHSIG`, Guardian
capability loss followed by lease expiry, Broker stall, Broker death and Shim
stall.  The signal matrix covers every Linux signal number `1..64` except the
two non-blockable signals `SIGKILL` and `SIGSTOP`, both before and after Broker
receive, plus ten post-Ready handler/unmask/`SA_RESTART` and signal-generation
syscalls ending in whole-TGID `SIGSYS`.  The Request-TID matrix proves
non-request-TID progress while the request TID remains kernel-blocked, both
with healthy-Broker PIDFD kill and Broker-stall lease expiry.

TLH-014 uses a separately compiled, temporary two-hook BPF-LSM observer.  It
does not alter Guard decisions and has its own one-entry map.  Each of the 19
negative handoff scenarios is moved into the observer Cgroup before exec; all
`19 x 32` records independently report zero successful AF_UNIX/SEQPACKET
runtime-socket creations and zero `sendmsg` calls.  The temporary programs,
links, map and bpffs mount are required to return to the exact baseline after
each observer run.

MFD-010 uses a separate one-hook `file_ioctl` BPF-LSM observer.  At the
external `FIONREAD` snapshot following each Seccomp-killed liveness-writer
operation, all `9 x 32` records report zero available bytes, `head == tail`,
one reader, zero writers and exactly one remaining pipe file.  This directly
binds null pipe bytes, null occupied pipe pages and null temporary writer-file
state to kernel BTF fields.  Its BPF objects and mount are also fully torn
down after every matrix.

Final build identities are:

| Artifact | SHA-256 |
|---|---|
| Guard BPF object | `38a6010b1c336a9f1c62f47ef27cf5e5ce5b878344d9c4d02001f314b056b3a5` |
| Handoff observer BPF object | `8529b8112fe088ac10cc83567a3afc8c0688b17c9f7fc1b526cf58bd72a20338` |
| Liveness observer BPF object | `4dafb756197aeaeffbb7c87db3f09b43a49c29b3244c396ae55ff2c7cf0f6912` |
| Native fault fixture | `861a0d5ed5a68618efac4b2ea3efad46ce6997b6b81771d61463f85aff09a93d` |

Final source identities for the Continuation-10 edit surface are:

| Path | SHA-256 |
|---|---|
| `live_l1/core/terminal_persistence_worker.py` | `04df9a859bf1c00bc2f521163b597fc159dfefd81e05c9c2cebdffe0792cb86a` |
| `tests/live_l1/test_terminal_persistence_worker.py` | `b4b92483ede1e53661ee265b86f2d92a919b8a82da9283c9fe1730355b728b41` |
| `live_l1/tools/validate_terminal_lease_capability.py` | `6ae3906ee37ce0fa1cd4b7f9a650939e1d21d9fdea8fd98b28b4efcfc2665722` |
| `live_l1/native/terminal_runtime_socket_lsm_guard.bpf.c` | `59eaf1390c47881e7e44321715b4bbcfa0cfb456965513725745077a17e4e2e8` |
| `live_l1/native/terminal_lease_fault_fixture.c` | `f317efe03c46772b9eaf42aa26684d3ac5fb11c2045bab6f4503904980c30a49` |
| `tests/live_l1/test_terminal_lease_capability.py` | `a93240c17a67212540f5502448a851e19ba8d2178e8aeafc0833e1e4d1561e61` |

### 10.2 Final suite status

```text
focused_capability_and_worker:7/7_PASS
full_tests_live_l1:373/373_PASS
full_tests_regression:170/170_PASS
AST_parse:PASS
git_diff_check:PASS
native_fixture_compile_Werror:PASS
```

### 10.3 Remaining blocking clauses and required environment

Exactly three clauses remain BLOCKED:

```text
R21-TLH-012  all Yama modes other than ptrace_scope=1
R21-SDL-013  real suspend/resume self-death series
R21-RES-015  complete external per-trial kernel timestamp manifest
```

`R21-TLH-012` must not be executed on the current long-lived WSL instance.
Linux Yama `ptrace_scope=3` cannot be lowered again before reboot.  The next
run therefore requires a disposable, snapshot/reboot-capable Linux VM or WSL
distribution with the same kernel/config/BTF/BPF-LSM envelope.  Modes `0`,
`2` and `3` must each be injected for exactly 32 probes; mode `3` is run last,
and the guest is then rebooted or discarded before returning to the required
positive mode `1`.

`R21-SDL-013` requires real host suspend/resume.  Cgroup freezer, `SIGSTOP`,
VM pause without guest suspend, or a wall-clock jump is not accepted.  The
guest must preserve the armed `CLOCK_BOOTTIME` kernel timer across system
suspend and externally prove the pending/fatal `SIGKILL` on resume for all 32
phase points.

`R21-RES-015` requires an external observer record for every required kernel
timestamp of every trial.  Aggregated maxima, percentiles, fixture-generated
timestamps or reconstructed timestamps are not accepted.  The timestamp
observer must be independently scoped, emit a complete per-trial manifest,
fail on any missing/duplicate point and run again under the full resource
cross-product.

Until all three rows pass in one regenerated `97/97` ledger, governance must
retain all eight macro entries, keep
`full_revision21_saturation_claimed:false`, deny the authorizing full run and
keep `I2_RESULT:BLOCKED`.  Independent Review and I3 remain prohibited.

## 11. Continuation 10 — RES-015 external kernel timestamp closure

Continuation 10 subsequently implemented and kernel-real verified
`R21-RES-015`.  The resulting Revision-21 ledger is `95/97 PASS`; it remains
deliberately `BLOCKED`, retains all eight macro entries and does not claim full
Revision-21 saturation.

The implementation adds a separately compiled and independently attached
BPF-LSM timestamp observer.  The observer is bound to the disposable Resource
Cgroup and the Resource run kind, timestamps only the exact trial markers with
`bpf_ktime_get_boot_ns`, and stores the complete scenario/trial/point identity,
Cgroup identity, TGID/TID and observation count.  The external manifest
validator rejects every missing, duplicate, unexpected, identity-invalid or
non-monotone record before the Capability JSON can serialize RES-015 as PASS.

The full kernel-real run used exactly:

```text
CAPABILITY_OUTPUT_ROOT:/tmp/iu4-cap-v14-cont10-res015-kernel-real-20260819-1
CAPABILITY_V14:BLOCKED
FOUNDATION_RESULT:PASS
CANDIDATE_PROFILE_FINGERPRINT:99758e5eb5ac730fbb60a0cb6a79caba4f0fbc7105de2074801b9bf67cbe935e
CAPABILITY_JSON_SHA256:b274a28185fa1811275c68875cda598d61634d9de0695a0261cdb5a1fff34513
REVISION21_COVERAGE_FINGERPRINT:aad327d3c492322c0c5469c35ad5c6f9e1e2dcbad72a4fd926ef54002e240930
REVISION21_COVERAGE_PASS_BLOCKED:95/2
REVISION21_BLOCKED_IDS:R21-TLH-012,R21-SDL-013
REVISION21_MACRO_REMOVAL_AUTHORIZATION:DENIED
FULL_REVISION21_SATURATION_CLAIMED:false
```

The external per-trial kernel timestamp result is:

```text
R21_RES_015_STATUS:PASS
TIMESTAMP_SOURCE:bpf_ktime_get_boot_ns
TIMESTAMP_SCENARIOS:8/8
TIMESTAMP_TRIALS_PER_SCENARIO:10000/10000
TIMESTAMP_RECORDS:260000/260000
TIMESTAMP_MISSING_RECORDS:0
TIMESTAMP_DUPLICATE_RECORDS:0
TIMESTAMP_UNEXPECTED_RECORDS:0
TIMESTAMP_INVALID_IDENTITY_RECORDS:0
TIMESTAMP_NONMONOTONE_TRIALS:0
TIMESTAMP_MANIFEST:/tmp/iu4-cap-v14-cont10-res015-kernel-real-20260819-1/external_kernel_timestamp_manifest_v1.json
TIMESTAMP_MANIFEST_SHA256:e00ce369fa9f25ac639f72e83b68871d19565effa16b3ead1a52ef6a583ff174
TIMESTAMP_MANIFEST_SIZE_BYTES:46982497
TIMESTAMP_OBSERVER_OBJECT_SHA256:866329d468209773cde0df7d0fb768e2604bf6202685e5c97833888dd0982b8f
```

Two preceding kernel-real focused runs proved the observer and all producers
at two trials each.  The generic marker/manifest smoke produced `52/52 PASS`
with manifest SHA-256
`27963ecc023d87c3a0128c3ed50d372502f2f635002b0fb234a7ecb63b80c7f5`;
the seven Native producer paths plus the Python Runtime-Channel path produced
`52/52 PASS` with manifest SHA-256
`421186915562112209f212a2682cb7a3d06ff1260560c15ad62b8e5d5aad253f`.

Final source identities for the RES-015 edit surface are:

| Path | SHA-256 | Lines |
|---|---|---:|
| `live_l1/native/terminal_runtime_socket_lsm_guard.bpf.c` | `b1ee2ce4367d26296a9c55d4883088bb731e4881efd700e040e197377d9db80c` | 79 |
| `live_l1/native/terminal_lease_fault_fixture.c` | `cabe4df827f6054835d2fa90c6d67a69c41d53e3719be9e430da6c35da7cd6e7` | 2,487 |
| `live_l1/native/terminal_native_trip_broker.c` | `b8ece4289c1ca92e5e9ce75309b456e4e42c17ec0cee1b12aa3c055af79cc936` | 21 |
| `live_l1/tools/validate_terminal_lease_capability.py` | `8735b8d571422b911fbac2bd453450634b6ccda412b8535a273f30c4c949e7c6` | 6,493 |
| `tests/live_l1/test_terminal_lease_capability.py` | `8fc2d3bb5b9fc01780c6c78f77b776c144ad2bd53de401c08573a6bc0a30004d` | 146 |

Post-change verification is:

```text
focused_capability_and_worker:8/8_PASS
full_tests_live_l1:374/374_PASS
full_tests_regression_venv:170/170_PASS
AST_parse:PASS
git_diff_check:PASS
native_fixture_and_broker_compile_Werror:PASS
timestamp_BPF_compile_Werror:PASS
timestamp_cgroup_released:PASS
timestamp_bpffs_unmounted:PASS
timestamp_programs_released:PASS
```

The non-binding System-Python regression diagnostic lacked NumPy and was
discarded; the binding rerun used the repository `.venv` required by
`AGENTS.md` and passed `170/170`.

Exactly two clauses remain BLOCKED:

```text
R21-TLH-012  Yama ptrace_scope modes 0, 2 and 3 at 32 probes each
R21-SDL-013  real host suspend/resume self-death series at all 32 phase points
```

Both remaining clauses require the separately specified disposable,
snapshot/reboot-capable and real-suspend-capable Linux host.  They must not be
executed on the current long-lived WSL instance.  Until both pass in the same
regenerated `97/97` ledger, governance must retain all eight macro entries,
keep `macro_removal_authorization:DENIED`, deny the authorizing full run and
keep `I2_RESULT:BLOCKED`.  Independent Review and I3 remain prohibited.

## 12. Continuation 10 — disposable-host closure and final authorization

Continuation 10 closed the final two atomic clauses on a separately
provisioned disposable Linux host and then completed the governance-authorized
full run.  The earlier BLOCKED statements in Sections 10 and 11 are retained
as chronological evidence and are superseded by this section.

### 12.1 Qualified disposable host

The host was an Ubuntu 26.04 QEMU `ubuntu-q35` guest with ACPI S3 explicitly
enabled, six virtual CPUs, 6 GiB RAM, OVMF and a read-only 9p mount of the
canonical repository at `/home/benja/projects/sniper-bot`.  Qualification
proved:

```text
QEMU_VERSION:10.2.1
ACCELERATOR:TCG
GUEST_KERNEL:7.0.0-28-generic
GUEST_ARCHITECTURE:x86_64
ACTIVE_LSM:lockdown,capability,landlock,yama,apparmor,bpf,ima,evm
MEM_SLEEP:s2idle [deep]
POWER_STATE:freeze mem disk
CANONICAL_REPOSITORY_MOUNT:9p read-only
OFFICIAL_UBUNTU_IMAGE_SHA256:9dc7c5363c0146a08ba0c9aa834d82c2c6dfbb1c471ad9a2f0aba1189e21be05
```

An independent S3 smoke observed QMP `SUSPEND`, status `suspended`, QMP
`WAKEUP`, status `running`, an unchanged boot ID, `PM: suspend entry (deep)`,
`ACPI: PM: Waking up from system sleep state S3` and `PM: suspend exit`.

### 12.2 R21-TLH-012 — Yama 0/2/3

One fresh guest boot executed Yama in the irreversible order `0, 2, 3`, with
mode 3 last.  Every mode emitted exactly 32 native records.  All 96 records
proved the OPEN gate blocked and independently reported zero runtime socket
creations and zero `sendmsg` calls:

```text
YAMA_BOOT_ID:724f141b-56d7-4b3a-8084-ad15d76bbd87
YAMA_MODE_ORDER:0,2,3
YAMA_PROBES_PER_MODE:32/32
YAMA_TOTAL_PROBES:96/96_PASS
YAMA_RUNTIME_SOCKET_CREATIONS:0
YAMA_SENDMSG_CALLS:0
YAMA_EVIDENCE:/tmp/iu4-host-closure-vm-20260819/yama-evidence-v2.json
YAMA_EVIDENCE_SHA256:b69f865c9d027aa7bdc315505e66b6efcb3a6756eb1aebc77c78f48d0c418979
```

The guest was discarded after mode 3; it was not reused for a positive
Yama-1 run.

### 12.3 R21-SDL-013 — real suspend/resume at 32 phase points

A separate fresh guest boot executed all phase points `0..31`.  At every
phase the native fixture armed an absolute `CLOCK_BOOTTIME` POSIX timer with
a two-second expiry and `SIGKILL`, durably emitted its ready record, directly
entered `deep` through `/sys/power/state`, and was externally observed in QMP
status `suspended`.  The host held suspend for more than the timer expiry,
issued `system_wakeup`, observed QMP `WAKEUP` and `running`, and verified the
target's `SIGKILL` result plus the three kernel S3 records.

```text
SUSPEND_BOOT_ID:8d878c5f-08e3-4839-a737-3b19a54b12da
SUSPEND_PHASE_POINTS:32/32_PASS
TIMER_CLOCK:CLOCK_BOOTTIME
TIMER_EXPIRY_NS:2000000000
MINIMUM_HOST_SUSPEND_HOLD_NS:3000000000
SLEEP_STATE:deep
FATAL_SIGNAL:SIGKILL
SUSPEND_EVIDENCE:/tmp/iu4-host-closure-vm-20260819/suspend-evidence.json
SUSPEND_EVIDENCE_SHA256:3cb00529931d9d06275aa14178a5eda104673574f2612b17dd7c890ba7381c09
```

The strict merged evidence object contains exact fields, exact record counts,
QMP event timestamps, guest boot identities, kernel power records, native
fixture output and binary/source identities.  The capability validator
accepted it without normalization or reconstruction:

```text
HOST_CLOSURE_EVIDENCE:/tmp/iu4-host-closure-vm-20260819/host-closure-evidence.json
HOST_CLOSURE_EVIDENCE_SHA256:83f54a0d47a60df22f0e45395e59ae74c784f088033c1ba9dbf3f11cd5ebd491
HOST_CLOSURE_STRICT_VALIDATION:PASS
COLLECTOR_SHA256:78b40014aa5660b0ca976033d7e712e4d0103e12775822f6471937dc71836099
FIXTURE_SOURCE_SHA256:88733165949d9f0fecb9f195c548beface25ab5ff88cacadac6eeaafd344f62b
FIXTURE_BINARY_SHA256:63bc67774afa5c1fb7eff5d5b3860cb83f59adccafd36f1041c82255308b4edd
```

### 12.4 Governance preflight

Before any authorizing full run, the validated host-closure result was bound
to the prior RES-015 kernel-real Capability result and the one-to-one ledger
was regenerated in the root context required to resolve every external
artifact identity.  This was the first authorization point:

```text
REVISION21_PREFLIGHT_CLAUSES:97
REVISION21_PREFLIGHT_PASS_BLOCKED:97/0
REVISION21_PREFLIGHT_BLOCKED_IDS:[]
REVISION21_PREFLIGHT_MACRO_REMOVAL_AUTHORIZATION:AUTHORIZED
REVISION21_PREFLIGHT_COVERAGE_FINGERPRINT:f9fc450aeb3c66c91af22dd41326612d3ad1be3eda084456ac730f8ae86d5e3a
```

No authorizing full run was started before that result.  At `97/97`, the
validator's governance transition became eligible to remove the eight
serialized Missing entries and set full Revision-21 saturation true.

### 12.5 Authorizing full run

The final successful run executed in a private mount namespace, with no QEMU
load and with exactly 10,000 certification trials and 32 startup probes:

```text
CAPABILITY_OUTPUT_ROOT:/tmp/iu4-cap-v14-cont10-host-closure-authorizing-20260820-6
CAPABILITY_V14:PASS
FOUNDATION_RESULT:PASS
CANDIDATE_PROFILE_FINGERPRINT:12ee335fc0afa07452d2fe28563baccf726142314613d9a9bac3870104349b88
CAPABILITY_JSON_SHA256:7baa6b2885567ce0b07a7b863f96b3c18a97a178aefe6535a5da8b8446a153ac
REVISION21_COVERAGE_PASS_BLOCKED:97/0
REVISION21_BLOCKED_IDS:[]
REVISION21_COVERAGE_RESULT:PASS
REVISION21_COVERAGE_FINGERPRINT:8c81ed8dd7ac03bbaaf93c4911156cec4fe6dadff5b0e6f1b380a27dd24a5cd3
REVISION21_MACRO_REMOVAL_AUTHORIZATION:AUTHORIZED
MISSING_MANDATORY_SCENARIOS:[]
FULL_REVISION21_SATURATION_CLAIMED:true
```

All eight macro-family statuses are `PASS`.  Their names remain in the
machine coverage vocabulary, but all eight historical serialized Missing
entries are removed from the final Capability evidence.

The complete external Resource timestamp manifest was regenerated inside the
same authorizing run:

```text
TIMESTAMP_SOURCE:bpf_ktime_get_boot_ns
TIMESTAMP_SCENARIOS:8/8
TIMESTAMP_TRIALS_PER_SCENARIO:10000/10000
TIMESTAMP_RECORDS:260000/260000
TIMESTAMP_MISSING_RECORDS:0
TIMESTAMP_DUPLICATE_RECORDS:0
TIMESTAMP_UNEXPECTED_RECORDS:0
TIMESTAMP_INVALID_IDENTITY_RECORDS:0
TIMESTAMP_NONMONOTONE_TRIALS:0
TIMESTAMP_MANIFEST:/tmp/iu4-cap-v14-cont10-host-closure-authorizing-20260820-6/external_kernel_timestamp_manifest_v1.json
TIMESTAMP_MANIFEST_SHA256:32dc3140965e4edf393bed9b287fe817e2e79a7b0b961e556b7bcaa4bc0ad878
TIMESTAMP_MANIFEST_SIZE_BYTES:47242504
```

Final authorizing Native/BPF build identities are:

| Artifact | SHA-256 |
|---|---|
| Native fault fixture | `63bc67774afa5c1fb7eff5d5b3860cb83f59adccafd36f1041c82255308b4edd` |
| Guard BPF object | `f8d631bfaff62400624108bf51a0d1d1c4ccea9efdd2adee6a17537925323de9` |
| Handoff observer BPF object | `70cb22b1d850063a093d0bc5b32fddc3a62a8cb040bfe19a2f923fe51bb078b9` |
| Liveness observer BPF object | `71dfc03b8c53ff0c8fe5657b38ec63b4f4e02c5f840d2ffaf5d20809b667feac` |
| Timestamp observer BPF object | `c67dbc67f5d1a13c4ff63bd1129f1a68b2e7e93f8ac1149bb674ab8a5e459f98` |

### 12.6 Host-compatibility and teardown hardening

The final implementation also:

- accepts the running kernel configuration only from `/proc/config.gz` or the
  distribution-standard `/boot/config-<release>`, while requiring the same
  three exact `=y` flags;
- treats only the generated `vmlinux.h` directory as a Clang system include,
  retaining `-Werror` for all IU4 BPF source;
- reads both the legacy direct `pipe_inode_info.head/tail` layout and the
  Kernel-7 anonymous `pipe_index` layout through CO-RE field-existence
  relocations;
- allows up to ten seconds only for temporary Observer BPF/RCU teardown
  observation; and
- allows up to 250 ms only for the external Liveness snapshot to observe
  Pipe HUP under saturation.  The separately measured and serialized 5-ms
  PIDFD/Liveness deadlines are unchanged.

The WSL CO-RE Liveness smoke emitted `288/288 PASS` exact kernel records.  The
Kernel-7 guest compiled the Liveness object with `-Werror`; its TCG timing was
correctly rejected for the full Resource deadline run and was not used as the
authorizing execution host.

### 12.7 Post-change verification and final scope

```text
focused_terminal_lease_capability:7/7_PASS
full_tests_live_l1:375/375_PASS
full_tests_regression_venv:170/170_PASS
AST_parse:PASS
native_and_four_BPF_compile_Werror:PASS
WSL_liveness_observer_kernel_records:288/288_PASS
authorizing_resource_cgroup_released:PASS
authorizing_bpffs_unmounted:PASS
authorizing_programs_released:PASS
authorizing_validator_process_released:PASS
disposable_QEMU_process_released:PASS
```

No real trading process, state, journal, scheduler, Exchange or Live path was
entered.  No Git mutation was performed.  Foreign artifacts and processes
were not cleaned or altered.  The excluded bundle script was not read,
executed or modified.  Independent Review was not started and I3 was not
entered.

```text
IMPLEMENTATION_PACKAGE:I2_ONLY
I2_RESULT:PASS
FOUNDATION_IMPLEMENTATION_RESULT:PASS
TERMINAL_LEASE_CAPABILITY_V14_RESULT:PASS
INDEPENDENT_REVIEW_STARTED:NO
I3_ENTERED:NO
```
