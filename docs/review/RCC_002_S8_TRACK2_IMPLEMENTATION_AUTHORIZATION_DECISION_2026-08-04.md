# RCC-002 S8 Track 2 Implementation Authorization Decision

| Field | Value |
|---|---|
| Decision ID | `RCC-002-S8-TRACK2-IAD-001` |
| Decision date | `2026-08-04` |
| Decision class | Exact bounded implementation authorization |
| Repository baseline | `7ab00e06e91c35e5738698c25fa941fa50516fa0` |
| Controlling proposal | `RCC-002-S8-TRACK2-CAP-001` |
| Controlling proposal SHA-256 | `c4c93a48dfac32098d30af88b60f389a81c1fb3f6059f1327f8c02dd38218588` |
| Independent proposal-review verdict | `APPROVE` |
| Independent proposal-review SHA-256 | `b26f2e037a7df59aeef405f7874350cfae014ad03082b2d15d85dad22cb35da5` |
| Inspection report SHA-256 | `b6df563815d1fc077f585511f9a9e779793e9869acb9ca8830d426d1a23b1ec1` |
| Original inventory SHA-256 | `c5925ad40fb6609f60fb98a6afcf482b31463a3e65858e4e1c3e22adb7b9b885` |
| Original ledger SHA-256 | `47ef3f5aa9cd573cb9c7188192e2cb5755022c38e0c1d5730c1417be1e014d27` |
| Original summary SHA-256 | `47caaf9d74530e89d3e3d1eeda595a4f9a15e1379329dcd43169aa76e2c7311c` |
| Authorized mutation paths | `8` |
| Required unchanged Track 2 paths | `25` |
| Protected-builder authority | `None` |
| Staging authority | `None` |
| Commit authority | `None` |
| Push authority | `None` |
| Status | `AUTHORIZED SUBJECT TO ACTIVATION CONDITIONS` |

## 1. Decision

The reviewed correction architecture identified by
`RCC-002-S8-TRACK2-CAP-001` is approved for one bounded implementation cycle.

This decision authorizes modification of exactly eight Track 2 paths and
creation of exactly six governance evidence paths, subject to every control and
activation condition in this decision.

No other repository mutation is authorized.

## 2. Activation conditions

This authorization is not active merely because this document exists.

Before any Track 2 implementation, import, compilation, or test execution:

1. this decision and its six controlling untracked governance and evidence
   documents must be committed in one controlled governance commit;
2. that governance commit must be pushed to `origin/main`;
3. local `HEAD`, `origin/main`, and remote `main` must be identical;
4. the index must be empty;
5. there must be no tracked worktree changes;
6. the original 33-file Track 2 ledger must still verify;
7. the protected builder must remain unaccessed;
8. no Track 2 byte may have changed.

Until all eight activation conditions pass, Track 2 implementation, import,
compilation, and testing remain unauthorized.

## 3. Exact authorized mutation scope

The following eight paths are the complete implementation mutation allowlist:

1. `rcc002/s8/manifests/common.py`
   - pre-correction SHA-256: `412d08de7683b87c9c433f09e0dcbdfe4f8e1126db908a3288fd7dc42bf35fdd`
   - pre-correction mode: `644`
   - pre-correction bytes: `5232`
2. `rcc002/s8/manifests/dataset.py`
   - pre-correction SHA-256: `1d9ee6b4e61002da03449abaf85f4b667f0f55badc5ddd1af5c31d18c0b26c02`
   - pre-correction mode: `644`
   - pre-correction bytes: `8295`
3. `rcc002/s8/reconciliation.py`
   - pre-correction SHA-256: `08ea39d0570db5d384b7fb5254ca4c119330b54121344e5d9dac7b90c02bac23`
   - pre-correction mode: `644`
   - pre-correction bytes: `4715`
4. `rcc002/s8/specification_profile.py`
   - pre-correction SHA-256: `c36d641936d64a6e4f9e75d26d93038d1f69f46e780bb3fbcf0ddcc16e548904`
   - pre-correction mode: `644`
   - pre-correction bytes: `2639`
5. `rcc002/s8/views.py`
   - pre-correction SHA-256: `958f60cfab1be1a1a37266d4c2332e62ba86647f4a889b8c7e41115db5d6e87c`
   - pre-correction mode: `644`
   - pre-correction bytes: `7957`
6. `tests/rcc002/s8/test_manifests.py`
   - pre-correction SHA-256: `cc155ef43301eda9b5c28be0c140a4d5f6c0cdf347d1050af260ae0529d17e46`
   - pre-correction mode: `644`
   - pre-correction bytes: `19760`
7. `tests/rcc002/s8/test_reconciliation.py`
   - pre-correction SHA-256: `66af42ec4c98f47b099030747b2b7a9104e7370bcb78d21f8eb60f561819da28`
   - pre-correction mode: `644`
   - pre-correction bytes: `5495`
8. `tests/rcc002/s8/test_views.py`
   - pre-correction SHA-256: `95d28f4a1fe27cecd940ef4a29e0df5ff74a39d57de52172f72ea3db6971e3f5`
   - pre-correction mode: `644`
   - pre-correction bytes: `7375`

No ninth Track 2 implementation or test path may be modified.

## 4. Exact required unchanged Track 2 scope

The following 25 Track 2 paths must remain byte-identical to the original
inspection ledger:

1. `rcc002/s8/__init__.py`
   - required SHA-256: `2a325b35a31436e1853d05e3a9d399d1e8beddd6778c4781c1b60ffcb69cd93f`
2. `rcc002/s8/artifact_class.py`
   - required SHA-256: `be9acaa776ebe97ea1460a4168d77cea9e04f556291749b0cf097b42c7a3839a`
3. `rcc002/s8/canonical.py`
   - required SHA-256: `0555077499e63d5be864de5e623c846cae70b55832fc6a5ece2ea513b53b56a9`
4. `rcc002/s8/field_registry.py`
   - required SHA-256: `8f3aa92fcb71444e5a2af2269fc11bd4d6a03f87b34dcb4aab0245cef5a44207`
5. `rcc002/s8/identity.py`
   - required SHA-256: `b104f40a0f30fd15a41af1c5234c6851b9ca95e005d6c99e97f95542f9ee5632`
6. `rcc002/s8/manifests/__init__.py`
   - required SHA-256: `7a2c8c46ea2862880fe0b8480e86ef8d08c767f47b003e0b0bbc69d0d62a4154`
7. `rcc002/s8/manifests/reproduction.py`
   - required SHA-256: `c212598e7b0859b3e3ee490ed36619929cfa8afad2ed13d0f93d3b58be3d887a`
8. `rcc002/s8/manifests/review.py`
   - required SHA-256: `8601132b6b7d0a936c4c2e2521471da576329ef785f582f8af180f77d1e33f26`
9. `rcc002/s8/manifests/run.py`
   - required SHA-256: `224978e0e647ba800520ceb5982905de32841d0d20dde0b4dcd7d5d2f4c94994`
10. `rcc002/s8/manifests/source.py`
   - required SHA-256: `6f3c2b25e8b497d8d6dc8e6b026770bce8040034c373e355427ccfb4994e03ed`
11. `rcc002/s8/manifests/stage.py`
   - required SHA-256: `1f9ce67af52c32f08627277d21ac230e4c73abbf1ce33716675fb1717c9ba608`
12. `rcc002/s8/projection.py`
   - required SHA-256: `26c0703f4ee480429e5aab1c64c2fcb2d3415f4e2faeb52f542596b598723b14`
13. `rcc002/s8/publication.py`
   - required SHA-256: `328b8416628617d66dab3362ff3970717e13ce0e55c3acc505011c5616dab8da`
14. `rcc002/s8/reason_codes.py`
   - required SHA-256: `174122a2773ec46f78754f807b2b65384d25972d7e7306db632f1ba1d5bceb6e`
15. `rcc002/s8/states.py`
   - required SHA-256: `99b8c804609414d0d8a5edee8dca0622f2ee3737997ea4ec754ef5776e4e6661`
16. `rcc002/s8/validation.py`
   - required SHA-256: `d7a98bd2111929c961854863261f2b019f4be6c0d845bcfec37c84fb04892de2`
17. `tests/rcc002/s8/__init__.py`
   - required SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
18. `tests/rcc002/s8/test_artifact_class.py`
   - required SHA-256: `fbfbf6a16cebf170992bbd277da713f22865511c4d9041598a96ff7b7d4d4eb6`
19. `tests/rcc002/s8/test_canonical.py`
   - required SHA-256: `4a3ad835aa21aa4dd2ff722d34a3a92a6220e006b64f18993e5b5d90103332fc`
20. `tests/rcc002/s8/test_field_registry.py`
   - required SHA-256: `f6d18216d707e8857bb4d8243e1b5b1e1bcb16eccb9019bb08e99c4efdfc922b`
21. `tests/rcc002/s8/test_identity.py`
   - required SHA-256: `8a3aa755c621178ae07d274eddcb7eda0aab3dbaae46e9b944c1bb94d1319060`
22. `tests/rcc002/s8/test_projection.py`
   - required SHA-256: `85f54aeccf9807cf2b803d2cf93f11fd8c7209c6f49e3bc9a610709318eec4bc`
23. `tests/rcc002/s8/test_publication.py`
   - required SHA-256: `0766235dce20f439d5f97132653456c0b1892f2baf17b3d2ad67002382dca6a3`
24. `tests/rcc002/s8/test_states.py`
   - required SHA-256: `2e117d06f1a976907503ef0e01ec6705cb18db3a2677d4db2639302c0d0d3bc5`
25. `tests/rcc002/s8/test_validation.py`
   - required SHA-256: `3e20114553729555aba07631bacea2f89b13dd48aabd858754e5f267562dd0b4`

Any byte change to an unchanged path invalidates this authorization.

## 5. Authorized correction responsibilities

### 5.1 Dataset Manifest correction

Authorized files:

- `rcc002/s8/manifests/common.py`
- `rcc002/s8/manifests/dataset.py`
- `tests/rcc002/s8/test_manifests.py`

Required result:

- prospective Dataset Manifest production version is exactly `1.0.2`;
- withdrawn versions `1.0.0` and `1.0.1` are rejected;
- schema ID, schema version, and schema reference agree;
- historical immutable evidence remains unchanged;
- source-string inspection is replaced by behavioral verification.

### 5.2 View fingerprint correction

Authorized files:

- `rcc002/s8/views.py`
- `tests/rcc002/s8/test_views.py`

Required result:

- the placeholder fingerprint construction is removed;
- the exact DP `0.9.0` Section `7.9.5` 11-key preimage is used;
- the preimage is serialized through the required RFC 8785/JCS path;
- SHA-256 is calculated over the exact canonical bytes;
- independent golden-vector and negative-variation evidence is provided.

### 5.3 Specification-profile correction

Authorized files:

- `rcc002/s8/specification_profile.py`
- `tests/rcc002/s8/test_manifests.py`

Required result:

- Data Pipeline Specification version is exactly `0.9.0`;
- Reproducibility and Manifest Specification version is exactly `0.9.1`;
- paths, identifiers, versions, and hashes match the certified baseline;
- obsolete and mixed-version profiles are rejected.

### 5.4 Reconciliation correction

Authorized files:

- `rcc002/s8/reconciliation.py`
- `tests/rcc002/s8/test_reconciliation.py`

Required result:

- primary-key fields are derived from evaluated schema requirements;
- `provider` is included only when required;
- primary-key ordering remains deterministic;
- provider-specific and consolidated schemas are tested;
- missing, duplicate, and invalidly ordered key fields are rejected where
  normative.

## 6. Exact authorized governance evidence paths

The implementation cycle may create only these six new governance evidence
paths:

1. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_AUTHORIZED_SCOPE_V1.json`
2. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_PRE_IMPLEMENTATION_LEDGER_2026-08-04.txt`
3. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_GATE_RESULTS_2026-08-04.txt`
4. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_FINAL_INVENTORY_2026-08-04.txt`
5. `docs/review/evidence/RCC_002_S8_TRACK2_CORRECTION_FINAL_SHA256_LEDGER_2026-08-04.txt`
6. `docs/review/RCC_002_S8_TRACK2_CORRECTION_IMPLEMENTATION_REPORT_2026-08-04.md`

These paths may record authorization scope, pre-implementation identity,
verification results, final candidate identity, and the implementation report.

They may not contain generated datasets, deployment artifacts, or executable
code.

## 7. Authorized read and execution boundaries

After activation, the implementation cycle may:

1. read all 33 bound Track 2 files;
2. read tracked RCC-002 specifications, schemas, registries, fixtures, and
   certified Track 1 governance evidence required by the approved correction;
3. modify only the eight paths in Section 3;
4. create only the six evidence paths in Section 6;
5. compile the eight authorized implementation and test paths;
6. import the five authorized Track 2 source modules;
7. execute focused tests in the three authorized test modules;
8. execute the complete `tests/rcc002/s8` suite;
9. execute the complete `tests/rcc002` regression boundary;
10. execute deterministic positive and negative controls required by the
    approved proposal.

Execution authority is limited to verification of the approved correction.

No dataset generation, publication, deployment, paper execution, live trading,
or production use is authorized.

## 8. Required implementation controls

The implementation cycle must prove:

1. baseline identity before mutation;
2. exact eight-path mutation scope;
3. exact pre-correction hash for every authorized path;
4. verification of the original 33-file ledger;
5. byte identity of all 25 unchanged Track 2 paths;
6. no change to certified Track 1 files;
7. no access to the protected builder;
8. no access to unrelated untracked content;
9. successful compilation of the authorized scope;
10. successful imports of the authorized source modules;
11. successful focused tests for F-001 through F-005;
12. successful complete Track 2 tests;
13. successful complete RCC-002 regression tests;
14. deterministic positive and negative controls;
15. final 33-file inventory and SHA-256 ledger;
16. exact changed-path and unchanged-path proof;
17. no staged files;
18. no commit or push.

Every executable verification must report:

- `exit_code=0`;
- `failure_count=0`;
- `error_count=0`.

No failed control may be waived by narrative interpretation.

## 9. Protected builder

The following path remains outside every authorized scope:

`scripts/build_rcc002_spec_bundle.py`

It must not be opened, read, hashed, imported, executed, modified, staged,
committed, packaged, or used as evidence.

A protected-builder control may inspect only path-policy data. It may not access
the builder content or metadata.

## 10. Explicit exclusions

This decision does not authorize:

- modification of any path outside Sections 3 and 6;
- modification of schemas, registries, fixtures, specifications, certified
  Track 1 files, or `SHA256SUMS`;
- staging;
- commit;
- push;
- dataset generation or publication;
- paper deployment;
- live deployment;
- production use;
- unrelated refactoring;
- scope expansion inferred from test failure or implementation convenience.

Any required scope expansion invalidates this decision and requires a revised
proposal, a new independent proposal review, and a new authorization decision.

## 11. Completion boundary

After implementation and successful verification:

1. the candidate must be byte-finalized;
2. exact candidate identities and verification evidence must be captured;
3. one independent implementation-candidate review must be performed;
4. an `APPROVE` verdict is required;
5. a separate certification decision must bind the exact candidate bytes;
6. staging and commit require separate explicit authorization;
7. push requires separate explicit authorization.

This decision grants no authority beyond the bounded implementation and
verification cycle defined above.

AUTHORIZED SUBJECT TO ACTIVATION CONDITIONS
