# X1 Trade Inspector S5L Cross-Archive Signal Discovery Characterization Gate Evidence — 2026-08-14

Status: **PASS**

Branch: `codex/x1-trade-inspector-s5l-cross-archive-signal-discovery-characterization-gate-2026-08-14`

Base commit: `e5c92c3a6869d2a6b7dfbee8f34ba15ecca996f0`

## Scope

This gate freezes the current S5L cross-archive signal-discovery route before extraction from `tools/trade_inspector/inspect_trades.py`.

Bound production surface:

- `export_cross_archive_signal_discovery`.

Its existing discovery dependencies remain the already extracted `discover_signal_groups` and `discover_pair_groups` bindings from `tools/trade_inspector/feature_discovery.py`.

No production implementation, CLI dispatch, runtime input, archive, market data, generated repository artifact, IU4 mode, exchange, or live path changed while establishing the gate.

## Production identity

`tools/trade_inspector/inspect_trades.py` remained byte-identical throughout the gate.

SHA-256 before and after:

`23e980aaf8749103fbeb2abd1527585fda354e1428cd469eb0a6b8e5130d92c4`

| Binding | AST SHA-256 | Source-segment SHA-256 |
|---|---|---|
| `export_cross_archive_signal_discovery` | `fe7c3efd1e2931eed29def91e1178b6e6db9cb335c99354a01531244a827c086` | `a1a193b1dd6f7d065d1dec9ba0afb530a921f6820c06372ff35e849af4d3083a` |

Prepared characterization-test SHA-256:

`d7f824f220eaa9b6d940c4d249b9efd359186399fee60b5fabe19018e4b52334`

## Complete artifact contract

The three-row single-archive fixture binds 10 single-key group exports, 6 pair-key exports, all/top rollups, the manifest, and the Markdown summary.

| Artifact | SHA-256 |
|---|---|
| `cross_archive_signal_discovery_v7f_all.csv` | `aeaba1e6a26123d2153a4fa47974dc67eed32418484d12fcda6c588a9e0a6376` |
| `cross_archive_signal_discovery_v7f_by_entry_atr_signal.csv` | `86ed1b93cf4cd207514ac650676e12a0d2d610e16febece790a5a0be56570488` |
| `cross_archive_signal_discovery_v7f_by_entry_ma200_signal.csv` | `a2f625686cd0d8f90ad27075091c0c81346c08625e6194c851243d77f606b370` |
| `cross_archive_signal_discovery_v7f_by_entry_ma200_signal__entry_mfi_signal.csv` | `775b873d02770d6b82dbd8b7e60c01637d595b9741b0619fb1bd7092b45f0ca0` |
| `cross_archive_signal_discovery_v7f_by_entry_mfi_signal.csv` | `78f7f82147473f28fa6b8395ccb0d208506f7a9bd93b967df3410e59c9799e07` |
| `cross_archive_signal_discovery_v7f_by_entry_regime_label.csv` | `a86eb1a740746ee75bac2c89b6b03569be151a6b37e8ca165cac36d36caeff1a` |
| `cross_archive_signal_discovery_v7f_by_entry_regime_label__entry_atr_signal.csv` | `5b3026eeccdb6596a02d92f6b4d1985845675aed9071b05e684ca5b756a2ae67` |
| `cross_archive_signal_discovery_v7f_by_entry_regime_label__entry_risk_label.csv` | `562e07ea83daf01d7a590d4718e9cd613cf13a12f48a6bac3f4a2d46a871ac50` |
| `cross_archive_signal_discovery_v7f_by_entry_risk_label.csv` | `1552c744c787903f76dbe00c50543dc65bd7e1404c74c6c65f84e229fe712776` |
| `cross_archive_signal_discovery_v7f_by_entry_risk_label__regime_aligned.csv` | `f8b8c87c9ec64f7cb48859097b535259eab3cf415e4e90dca0269890bcbd1dbe` |
| `cross_archive_signal_discovery_v7f_by_entry_score_at_entry.csv` | `4960efe3ddd73abf4c8786472e5f277a50f3d2ced83b26a9114d9a8cb35f60ee` |
| `cross_archive_signal_discovery_v7f_by_entry_score_at_entry__entry_risk_label.csv` | `661422dbc734229b9286c604c9ee2e78897896cf97a7f575438429b166b989f0` |
| `cross_archive_signal_discovery_v7f_by_regime_aligned.csv` | `3dde810e5f7c1a7611edd417400004a8f42482611e61de264df0362bcb2770ef` |
| `cross_archive_signal_discovery_v7f_by_risk_good_at_entry.csv` | `490a6e56152fccc443791ee83d8ef21a933c6f715f0781a1df7ecd6d5ed0ad95` |
| `cross_archive_signal_discovery_v7f_by_trade_family.csv` | `ef118a0b22eb1e8eed869f6bd1d2e966c6d4a42b87621bf83bb8597c59dbc83c` |
| `cross_archive_signal_discovery_v7f_by_trade_family_group.csv` | `9525a9ce54a952a01227941a213fb60350289d7d7dd29d8e3973d6d733d4d46f` |
| `cross_archive_signal_discovery_v7f_by_trade_family_group__entry_risk_label.csv` | `8ec677dee40d2edbcc8893b5ea46e12062e89943f8fd45a570125b41fbbdd56e` |
| `cross_archive_signal_discovery_v7f_manifest.csv` | `d1b6fd1d2e99be2b959bb4437d6307bb805a2baa7483032bb6659488ac3b3783` |
| `cross_archive_signal_discovery_v7f_top.csv` | `aeaba1e6a26123d2153a4fa47974dc67eed32418484d12fcda6c588a9e0a6376` |
| `v7f_cross_archive_signal_discovery_summary.md` | `f6c0ba996665d62687947287f4f6fb88476cb203db47963a4f344c264e06ae5f` |

Canonical filename-to-hash fingerprint:

`e07b71e49bed90ac7618a15bb89b16eb5c09136637116cd545b21a72395811e2`

The complete fixture evaluates 16 groups. All rows remain `NOT_ACTIONABLE` with high warning, the route is `WARN`, and the top artifact is byte-identical to the all-groups artifact.

## Empty and boundary contracts

Empty input creates the same 20 filenames. The 18 derived CSV artifacts other than the manifest are zero-byte files. The empty manifest SHA-256 is `40f0bd5f1086b8ea2b15b80a004e04ee2802b09266aac8af0df89d3691f2f9df`; the empty summary SHA-256 is `3f4b5f13d3d5f38287ae3221f6a35c073d15a19f1471eaebb95d54c961551fb8`; and the complete empty filename-to-hash fingerprint is `43acf4c3008bf448036431de39f5ed16ffe9f8709c326a60a1e43ff7de19ab07`.

Three boundary fixtures prove the independent conditions:

| Rows | Source archives | Mode | Status | Statistical interpretation |
|---:|---:|---|---|---|
| 29 | 2 | `multi_archive_analysis` | `WARN` | `no` |
| 30 | 1 | `single_archive_infrastructure_validation` | `PASS` | `no` |
| 30 | 2 | `multi_archive_analysis` | `PASS` | `yes` |

Each unique-value boundary fixture produces 16 groups per input row. The all-groups artifact remains score-sorted; the top artifact contains exactly its first 50 rows.

## Current enrichment semantics

The gate deliberately freezes the current distinction between manifest scope and per-row enrichment:

- manifest `archive_count` reflects distinct non-empty source archive IDs;
- manifest mode becomes multi-archive at 2 distinct archives;
- every discovery row currently retains `archive_scope=single_archive_validation` and `archive_count=1`;
- every discovery row uses the function argument as `source_archive_id`;
- every discovery row receives the same threshold-derived statistical-interpretation flag.

This documents current behavior and does not authorize changing it during extraction.

## Filesystem and console contract

The gate binds recursive directory creation, route-owned overwrite, preservation and sorted listing of a foreign file, exact metric and file-list output order, exact path formatting, and empty stderr.

## Validation

Focused characterization:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest -v tests.trade_inspector.test_inspect_trades_characterization

Ran 63 tests
OK
```

Full regression:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests/regression -p 'test_*.py'

Ran 170 tests
OK
```

`git diff --check` passed.

## Safety and next step

Only characterization tests and this evidence document changed. IU4 ENFORCED, Live-L1, exchange, and live execution remain locked. No source data or runtime input was changed.

After integrating this gate into `main`, the next development step is the structure-only S5L extraction into a dedicated cross-archive signal-discovery module, preserving all bound semantics and facade bindings.
