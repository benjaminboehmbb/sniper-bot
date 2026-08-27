# Pre-IU-4 Workstation Full-History SHADOW Observation Authorization — 2026-08-17

## Status
**FÜRSTÜNDIGE UNTERLAGEN VORGELEGT, BEREIT FÜR FREIGABE**

## Request
`IU4-WORKSTATION-FULL-HISTORY-SHADOW-OBSERVATION FREIGEBEN`

## Authorization Decision
- Datum/Uhrzeit: `2026-08-17T08:27:40Z`
- Antragsteller: `benja`
- Genehmiger: `benja`
- Ergebnis: **APPROVED** 

## Preconditions (must all be true before run start)
1. Gate contract is in force from `docs/review/PRE_IU4_WORKSTATION_FULL_HISTORY_SHADOW_GATE_EVIDENCE_2026-08-13.md` (exactly one-shot, bounded, SHADOW/PAPER run).
2. Workstation host only: `WORKSTATION`.
3. Requested observations: `1,042,658` with `requested_max_ticks <= configured_max_records`.
4. Bound commit transferred to Workstation: `89e13fecd1ab549ca7099818b1c9ad4984cb6f7a`.
5. Immutable data/policy authorities:
   - Source CSV SHA-256: `2896badb62e3236df301a1ccf56b878916c48b22ff57483e86b9fc32bffaf104`
   - Normalized slice SHA-256: `902d10b1d7678777bd23140ff459b9c5eaa9ef7d968bab7ab6e09926bfbfba8a`
   - Throttle profile SHA-256: `b16566970a3d7db4b038085d0b8601e24721fae572fbe7d3159c071680cd91e7`
   - Canonical policy fingerprint: `ed6e55744ce76d4f2e159832a2aeebcd4dbeb0f5dc1cdbbfda6177af119d1ada`
   - 5m seed SHA-256: `6a07c0e6ca24cfd7b9e6bdea3562a7e505cf922e07a54c85dac6ff97473ef5e5`
   - Economics SHA-256: `f65f00038c9420d09b7f4a0f8c28cc81a7f38998cdce52fd4f1619f89cffbc86`
6. Safety fields are fixed to:
   - IU4 ENFORCED: `false`
   - Exchange: `false`
   - Live: `false`
   - source-state mutation: `false`
7. Resume from partial journal is **not** authorized for this action.

## Acceptance checks that must still pass post-run (complete 14-point list)
1) `process exit code = 0`, no runtime/traceback/failure markers  
2) `1,042,658/1,042,658` records processed, ordered  
3) observation sequence and tick IDs `1..1,042,658`  
4) `1,042,658/1,042,658` unique source-intent IDs and IU4 request IDs  
5) evidence fingerprint + journal count/bytes/SHA-256/chain-head validated, chain clean  
6) atomic source bytes/manifest/state fingerprint/transaction sequence unchanged  
7) market input + normalized hash unchanged pre/post  
8) approved throttle/economics/seed/repo/launcher/host bindings unchanged  
9) position-before/action/position-after parity on every record  
10) autonomous exits fully accounted as committed close or guard-divergence NOOP  
11) loss-cluster blocked entries represented as source BUY / observed HOLD / NOOP / FLAT→FLAT  
12) unbound autonomous-exit suppression = 0, hidden divergence = 0  
13) final positions final Legacy == final IU4 sandbox == FLAT  
14) SHADOW/PAPER safety fields remain exact (as above)

## Scope
This authorization covers only the bounded Workstation full-history SHADOW PAPER observation. It does **not** authorize IU4 ENFORCED, Exchange, Live, source-state mutation, or any resume authority.

## Note
No repository content is changed by this authorization artifact itself; it is evidence governance/ops control only.