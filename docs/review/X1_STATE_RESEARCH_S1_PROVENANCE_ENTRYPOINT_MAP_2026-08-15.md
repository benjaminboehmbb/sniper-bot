# X1 State-Research S1 Provenienz- und Entry-Point-Karte

Datum: 2026-08-15

Status: PASS (statischer Read-only-Audit)

Basis-Commit: `02671c5dbd77f7479ffbe32c7efabe6f5bb0fd03`

Audit-Branch: `codex/x1-state-research-s1-provenance-entrypoint-map-2026-08-15`

## Zweck und Grenzen

Dieser Audit inventarisiert die Provenienz, Ein- und Ausgaben sowie das Entry-Point-Verhalten aller 43 getrackten Dateien unter `scripts/state_research/`. Er verändert weder Rechenlogik noch Eingaben und führt keines der Forschungsskripte aus. Die Klassifikation beruht auf statischer AST- und Quelltextanalyse.

Die Ergebnisse autorisieren weder Archivierung noch Laufzeitaktivierung. IU4 ENFORCED, Live-L1, Exchange und Live bleiben gesperrt.

## Kohorten-Fingerprint

- Getrackte Python-Dateien: 43
- Gesamtumfang: 6.182 Zeilen
- Explizit durch `if __name__ == "__main__"` abgeschirmt: 21
- Ausführung bereits beim Import: 22
- Import-Zeit-Ausführer mit Datei-Outputs: 8
- Import-Zeit-Ausführer ohne Datei-Output, aber mit Berechnung/Stdout: 14
- Python-Importkanten in diese Kohorte: 0
- Markdown-Dateien mit Kohortenreferenzen: 9
- SHA-256 des geordneten SHA-256-Manifests: `b5223982b7fcf823289720c57ab0c04bd47161ec57c8de4fc970d3eddaf2efba`

Der Kohorten-Fingerprint wurde erzeugt, indem für jede von `git ls-files 'scripts/state_research/*.py'` in Git-Reihenfolge gelieferte Datei die normale `sha256sum`-Manifestzeile gebildet und anschließend der vollständige Manifesttext erneut mit SHA-256 gehasht wurde.

## Abhängigkeiten und vorhandene Evidenz

Es existiert keine Python-Importkante auf `scripts.state_research` oder `state_research`. Die Kohorte ist damit derzeit eine Sammlung eigenständig gestarteter Forschungsskripte und keine importierte Produktionsbibliothek.

Neun getrackte Markdown-Dateien referenzieren die Kohorte:

- `docs/inventory/REPOSITORY_STRUCTURE_INVENTORY_2026-06-06.md`
- `docs/inventory/REPOSITORY_USAGE_AUDIT_2026-06-06.md`
- `docs/inventory/X1_SCRIPT_INVENTORY_AND_QUALITY_AUDIT_2026-08-14.md`
- `docs/research/STEP20C_live_replay_spec.md`
- `docs/research/STEP20D_dynamic_exposure_scaling_spec.md`
- `docs/review/PRE_IU4_ANTIGRAVITY_INDEPENDENT_REVIEW_2026-08-09.md`
- `docs/review/PRE_IU4_CLAUDE_ANTIGRAVITY_REVIEW_PACKET_2026-08-09.md`
- `docs/review/PRE_IU4_REPOSITORY_QUALITY_AUDIT_2026-08-09.md`
- `docs/review/X1_TRADE_INSPECTOR_S5Z_FACADE_CLOSURE_AUDIT_2026-08-15.md`

Die vier zentralen festen Eingaben und der abgeleitete STEP18-Core-Input sind auf dem X1-Arbeitsstand nicht vorhanden:

- `live_logs/passive_shadow_risk_snapshots.csv`
- `live_logs/trades_l1_auto_analysis.csv`
- `live_logs/trade_lifecycle_snapshots.csv`
- `live_logs/trades_l1.jsonl`
- `reports/step18/step18_core_metrics.csv`

Das Fehlen ist kein Anlass, Quelldaten zu erzeugen oder zu verändern. Es bestätigt, dass die historischen Skripte hier nicht ausgeführt werden dürfen.

## Abgeschirmte STEP11- bis STEP15-Kohorte

Alle folgenden 21 Skripte besitzen einen expliziten Main-Guard. `$--…` bezeichnet einen obligatorischen oder konfigurierbaren CLI-Pfad; die tabellierten Standardpfade sind feste Defaults.

| Phase | Skript | Eingaben | Ausgaben | SHA-256 |
|---|---|---|---|---|
| STEP14C | `analyze_continuous_meta_state_score.py` | `$--recovery-detail` | `$--out-dir/continuous_meta_state_score_{correlations,detail,summary}_$--label.csv` | `77c1bacc40bc47cf6adf070cb14a19f6352aae1de3fa1930bc11a35bf60a6b7d` |
| STEP13F | `analyze_degradation_acceleration.py` | `$--persistence-detail`; `$--shadow-csv` | `$--out-dir/degradation_acceleration_{correlations,detail,summary}_$--label.csv` | `1eab777c764ad105b3d491381204be2f92801830f684c93d4bf6da8c2cf0f6c4` |
| STEP14B | `analyze_meta_state_scoring.py` | `$--recovery-detail` | `$--out-dir/meta_state_scoring_{correlations,detail,summary}_$--label.csv` | `928a6779964033464ae609fb0b88f151a2f8305ebc12d4ed7a3e73a1821e833a` |
| STEP11B | `analyze_passive_shadow_risk.py` | `live_logs/passive_shadow_risk_snapshots.csv` | drei `reports/passive_shadow_risk/passive_shadow_*_STEP11B_shadow_risk.csv` | `6bfae2ccc5c8e9bc0080d201ed42b3a365102e27a7899b02bc0ffc27457b8ee1` |
| STEP11B v2 | `analyze_passive_shadow_risk_v2.py` | Passive-Shadow-CSV; `live_logs/trades_l1.jsonl` | drei `reports/passive_shadow_risk/passive_shadow_v2_*_STEP11B_v2.csv` | `72db6f2494ed8d7726d036f3ef0630e4326c4173f08fe7ac7919fd2b65402b07` |
| STEP13 | `analyze_pre_toxic_transitions.py` | `$--persistence-detail`; `$--shadow-csv` | `$--out-dir/pre_toxic_transition_{detail,summary}_$--label.csv` | `b3a0a93615743a12db832331a357e22d06bad6c4c1bc941fd75e540aca5fece0` |
| STEP14 | `analyze_recovery_probability.py` | `$--persistence-detail`; `$--shadow-csv` | `$--out-dir/recovery_probability_{detail,summary}_$--label.csv` | `176e4cf29b51c8667d3b0e27ef8093713a7889e83fb9cb21f2463618563a5936` |
| STEP11C | `analyze_recovery_transitions.py` | Passive-Shadow-CSV; `live_logs/trades_l1.jsonl` | zwei `reports/passive_shadow_risk/recovery_transition_*_STEP11C_recovery_transitions.csv` | `aca236ed4a11218ca3a7abe2700a5304583eaee3dde0677607a14ccb8775a47a` |
| STEP13B | `analyze_safe_collapse_patterns.py` | `$--shadow-csv`; `$--transition-detail` | `$--out-dir/safe_collapse_{detail,summary}_$--label.csv` | `6f645c2704a5a167c06b6227310916e2999c6c7dc571f838952f3988de8114df` |
| STEP11B | `analyze_shadow_persistence.py` | Passive-Shadow-CSV; `live_logs/trades_l1.jsonl` | zwei `reports/passive_shadow_risk/shadow_persistence_*_STEP11B_persistence.csv` | `2e39db3209d6cd01738e0f07ae6250ff7d7fb84380a73c9ef1b2ff3f54a61818` |
| STEP14D | `analyze_snapshot_meta_state_score.py` | `$--persistence-detail`; `$--shadow-csv` | `$--out-dir/snapshot_meta_state_score_{correlations,detail,summary}_$--label.csv` | `ae885dd704f73bfb91466a173a4bb56eaa1e61c6c92dd931e68fe80377c8e6bb` |
| STEP11 | `analyze_state_factor_strength.py` | `$--persistence-detail`; `$--recovery-detail`; `$--v2-detail` | drei `reports/passive_shadow_risk/state_factor_strength_*_STEP11_factor_strength.csv` | `5896aa339c72433dea861b88b9bf28f585f5d7da5939a0e2d5e41889e10fb8b2` |
| STEP11C | `analyze_transition_momentum.py` | Passive-Shadow-CSV; `live_logs/trades_l1.jsonl` | zwei `reports/passive_shadow_risk/transition_momentum_*_STEP11C_transition_momentum.csv` | `c3d6f50d0a17444598aaea1c9390512691621ea257eaa50872ca0ec2573165d3` |
| STEP15 | `simulate_adaptive_position_sizing.py` | `$--snapshot-detail` | `$--out-dir/adaptive_position_sizing_{buckets,summary}_$--label.csv` | `be9fe9629ed55ed0c78cf7bde6fca264acc8df75b1a697ad982b9feac9b440bd` |
| STEP15C | `simulate_adaptive_position_sizing_variants.py` | `$--snapshot-detail` | `$--out-dir/adaptive_position_sizing_variants_summary_$--label.csv` | `9066d669d5f7143ee9b55e1c1f3231d2acd9c62f7c909918dc1c111b7fa48918` |
| STEP13E | `simulate_confirmed_toxic_exit.py` | `$--shadow-csv`; `$--trades-jsonl` | `$--out-dir/confirmed_toxic_exit_{detail,summary}_$--label.csv` | `6ad802bbccda98561ef79e4499f32eedf58e5613752493517bf98e938301608a` |
| STEP13C | `simulate_safe_collapse_exit.py` | `$--shadow-csv`; `$--trades-jsonl` | `$--out-dir/safe_collapse_exit_summary_$--label.csv` | `c6243bfe42a84c3516b0b47bb7abc389c7bd9364830b95ab366ffb682dfbd1d3` |
| STEP13D | `simulate_safe_collapse_partial_exit.py` | `$--shadow-csv`; `$--trades-jsonl` | `$--out-dir/safe_collapse_partial_exit_{detail,summary}_$--label.csv` | `d02a6ef36183b22498a4a16618b0826753bf0696af1e7025c7406c1a2cc55d5a` |
| STEP12 | `simulate_shadow_gates.py` | `$--factor-detail` | `reports/passive_shadow_risk/shadow_gate_simulation_STEP12_shadow_gate_sim.csv` | `41034d99673a43782812e8b428e90c91da4fc1680cd6f4762f75f521cdfdfba5` |
| STEP12B | `simulate_shadow_gates_no_lookahead.py` | `$--shadow-csv`; `$--trades-jsonl` | zwei `reports/passive_shadow_risk/shadow_gate_no_lookahead_*_STEP12B_no_lookahead.csv` | `95c21fcc4cd15ad1103f418f2f2217fa279ef926d32ac9e9b9d046bae957e14f` |
| STEP13G | `simulate_toxic_dominance_exit.py` | `$--shadow-csv`; `$--trades-jsonl` | `$--out-dir/toxic_dominance_partial_exit_{detail,summary}_$--label.csv` | `a8effd0cce0470c410efd9febdf8f7d5d3163bb78213188e9dcd7f5cfd9cd818` |

Diese Kohorte ist import-sicher im engen Sinn: Ein Import startet keine Analyse. Das ist keine Aussage über fachliche Validierung oder aktuelle Datenverfügbarkeit.

## Historische STEP18- bis STEP20E-Import-Zeit-Kohorte

Alle folgenden 22 Skripte führen beim Import bereits Dateizugriffe, Pandas-Berechnungen und/oder Ausgabeoperationen aus. Es gibt keinen Main-Guard. Ein Import ist daher ein Laufversuch und darf nicht als harmlose Inspektion behandelt werden.

| Phase | Skript | Eingaben | Ausgaben/Seiteneffekt | SHA-256 |
|---|---|---|---|---|
| STEP18 | `analyze_step18_buckets.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `42a1a0ba5c432c1ca00eef4b6416485a503a57db5825307ad857f70713919d44` |
| STEP18 | `analyze_step18_clusters.py` | `reports/step18/step18_core_metrics.csv` | vier STEP18-Cluster-CSVs | `ada1aea9358dff4b543a90e1ee1761ab39b6aec4623bbdb170825fb51dfcf0ce` |
| STEP18 | `analyze_step18_predictive_power.py` | Passive-Shadow-CSV | Stdout | `49f992538ada5ab7ce795aecdd33eced7b6d6e68199998eeb49292807b88e2ad` |
| STEP18 | `analyze_step18_trade_lifetime.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `8f235b82746faa50ebd4ea6bdd33104717ee6b821c92c46453299056db3e1600` |
| STEP18 | `build_step18_core_pipeline.py` | Passive-Shadow-CSV | erstellt `reports/step18`; schreibt fünf STEP18-Core-CSVs | `05bbf39e66bd87ede3902165c070847f25b86bee9c31f6d52a212b5f7d7a3ae9` |
| STEP19B | `analyze_step19B_real_exit_replay.py` | Passive-Shadow-, Lifecycle- und Trades-Auto-CSV | `reports/step18/step19B_real_exit_replay.csv` | `414fe6edbf7a315351b86f9973f2c633c0a055e448c30352ffe300c896686ffc` |
| STEP19B | `analyze_step19B_threshold_sweep.py` | Passive-Shadow-, Lifecycle- und Trades-Auto-CSV | Stdout | `98236fc02a9b65f85c7411e3d42d2caefe41bf06e0d4958542c498005db3e6fe` |
| STEP19 | `analyze_step19_blocked_trades.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `2b1f132f7de99f49a0af5c7a9a138fcf842ae2760d2d3b5bf52d86e957cd1c12` |
| STEP19 | `analyze_step19_blocked_winners.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `fee296edf91a8f38d41f1f57fb8fbc560d607968fa326c2a3e905bbfe45b6644` |
| STEP19 | `analyze_step19_dynamic_exit_replay.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `f13c4366b15cc59ce7db9329d269a17aa9aa9d09a04e343e7f35de0f029a3bb9` |
| STEP19 | `analyze_step19_entry_gate.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `fded5b2a284fcf311bbcb2285314a1a160d6e1cc988b0964a54aa94e0417ab5f` |
| STEP19 | `analyze_step19_gate_quality.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `3069392f6c459d2dc54db1278bfa575756228e007159b8da80dff91b9f9a11e8` |
| STEP19 | `analyze_step19_risk_escalation.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `2b0eafa4c5b8f94509b608d0ecc026ba5bc7f0032bf33459a9e9a1b639df1fe9` |
| STEP19 | `analyze_step19_shadow_gate.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `ae4d8d8fc8dccdc5fd454d6ed1069d44bb0abcbf06a6d6c4a8e3471feee07a0e` |
| STEP19 | `analyze_step19_shadow_gate_replay.py` | Passive-Shadow-CSV; Trades-Auto-CSV | zwei STEP19-Shadow-Gate-Replay-CSVs | `0a91b7e836679b3611c9650d1a3c1385768911329e266fdaff54681e16cc09ad` |
| STEP19 | `analyze_step19_threshold_fine.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `ece62b2ddeb36ab9668ddb66b1ca6abaa87afd0c7b38bb3f068e48b1773e316f` |
| STEP19 | `analyze_step19_threshold_sweep.py` | Passive-Shadow-CSV; Trades-Auto-CSV | Stdout | `20e0f9b1480915db12c7b9ca1c5d19bd8a316e6dae8687b002ced35f56ca0168` |
| STEP20C | `analyze_step20C_live_replay.py` | Passive-Shadow-CSV; Trades-Auto-CSV | `reports/step18/step20C_live_replay.csv` | `7c3f1488c565fad9c3cd72f401ce747d63e9ecfe4af982552271a09c0f3e2841` |
| STEP20D | `analyze_step20D_dynamic_exposure_scaling.py` | Passive-Shadow-, Lifecycle- und Trades-Auto-CSV | `reports/step18/step20D_dynamic_exposure_scaling.csv` | `04bdee183f4854753068851361867cc34283bd77204ac2af1e1adc51365c1fd0` |
| STEP20D | `analyze_step20D_sensitivity.py` | Passive-Shadow-, Lifecycle- und Trades-Auto-CSV | Stdout | `49f37fe4d47e3205e4f6b1eb57cc67330fe2a81258f18d832aa3b849268e7636` |
| STEP20E | `analyze_step20E_true_dynamic_exposure_replay.py` | Passive-Shadow-, Lifecycle- und Trades-Auto-CSV | `reports/step18/step20E_true_dynamic_exposure_replay.csv` | `14667ea1f44d380e807523a0a71402b3786eeafff306d7ee3e4a8f44d29438ee` |
| STEP20 | `analyze_step20_position_sizing_replay.py` | Passive-Shadow-CSV; Trades-Auto-CSV | `reports/step18/step20_position_sizing_replay.csv` | `b185c681497db4c83ea929b5fc8701d3e0d5fd37f097257c18dfafea9655e185` |

Pfadlegende: Passive-Shadow-CSV = `live_logs/passive_shadow_risk_snapshots.csv`; Trades-Auto-CSV = `live_logs/trades_l1_auto_analysis.csv`; Lifecycle-CSV = `live_logs/trade_lifecycle_snapshots.csv`.

## Fachlicher Evidenzstand

- STEP18 bis STEP20E bleiben laut bestehendem Inventar Review-Bestand; es gibt keine Archivierungsfreigabe.
- Für STEP20C existieren eine Replay-Spezifikation und eine historische Integrations-Gate-Beschreibung. Das ersetzt keine heutige Import-Sicherheits- oder Datenverfügbarkeitsprüfung.
- STEP20D v1 ist als Proof of Concept mit methodisch optimistischer, rückwirkender Anwendung des finalen Multiplikators dokumentiert.
- STEP20E korrigiert diese methodische Schwäche durch zeitabhängige Expositionsreduktion, wurde fachlich aber ausdrücklich nicht validiert.

## Risiken und Fail-closed-Folgerungen

1. Ein Import eines der 22 historischen Skripte ist eine Ausführung, nicht bloß eine Symbolinspektion.
2. Acht Skripte können getrackte oder ungetrackte Reportdateien überschreiben beziehungsweise neu anlegen.
3. `build_step18_core_pipeline.py` legt `reports/step18` bereits beim Import an, bevor es den festen, hier fehlenden Input liest.
4. Die festen Eingaben fehlen auf dem X1-Arbeitsstand. Ein Lauf wäre daher weder reproduzierbar noch durch diese S1-Evidenz autorisiert.
5. Keine Paritäts-, Fail-closed- oder Laufzeit-Gates werden durch diesen Audit verändert oder abgeschwächt.

## Ergebnis

S1 ist vollständig: Alle 43 Dateien sind mit Entry-Point-Klasse, Phase, Eingaben, Ausgaben und Quellhash gebunden. Die sichere Trennlinie verläuft zwischen 21 bereits abgeschirmten STEP11- bis STEP15-Skripten und 22 historischen STEP18- bis STEP20E-Import-Zeit-Ausführern.

## Nächster freigabepflichtiger Schritt

Nach der Branch-Integration dieser Evidenz folgt **X1-STATE-RESEARCH-S2-IMPORT-TIME-CHARAKTERISIERUNGSGATE**. Es bindet zunächst den kleinsten stdout-only Vertreter `analyze_step18_predictive_power.py` an statische Quell-/AST-Invarianten sowie fixture-basierte Missing-Input- und Ausgabeerwartungen, ohne das bestehende Skript gegen reale Daten auszuführen oder seine Mathematik zu ändern. Erst nach diesem Gate darf eine reine Entry-Point-Einkapselung (`main()` plus Main-Guard) separat umgesetzt werden.
