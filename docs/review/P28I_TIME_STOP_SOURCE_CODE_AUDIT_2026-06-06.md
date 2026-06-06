# P28I TIME-STOP SOURCE CODE AUDIT

Date: 2026-06-06
Device: G15 / AR15
Environment: WSL

## Objective

Inspect source code related to LONG_TIME_STOP_HIT and SHORT_TIME_STOP_HIT before applying any patch.

## live_l1/core/execution.py

exists: True

```text
13: # Current scope:
14: # - FLAT + BUY   -> OPEN_LONG
15: # - LONG + BUY   -> NOOP
16: # - SHORT + BUY  -> CLOSE_SHORT (+ trade log)
17: # - FLAT + SELL  -> OPEN_SHORT
18: # - SHORT + SELL -> NOOP
19: # - LONG + SELL  -> CLOSE_LONG (+ trade log)

20: # - HOLD         -> NOOP
21: #
22: # Added:

47: class ExecutionDecision:
48:     action: str
49:     executed: bool
50:     position_before: str
51:     position_after: str
52:     side_after: str
53:     entry_price: Optional[float]

54:     entry_timestamp_utc: str

55:     reason: str
56: 

57: 

212:         raise AttributeError("state.s2_position missing")
213: 
214:     if not hasattr(state.s2_position, "position"):
215:         state.s2_position.position = "FLAT"
216: 
217:     if not hasattr(state.s2_position, "size"):
218:         state.s2_position.size = 0.0

219: 
220:     if not hasattr(state.s2_position, "entry_price"):
221:         state.s2_position.entry_price = None
222: 
223:     if not hasattr(state.s2_position, "entry_timestamp_utc"):

224:         state.s2_position.entry_timestamp_utc = ""

225: 
226:     if not hasattr(state.s2_position, "position_size"):

227:         state.s2_position.position_size = float(getattr(state.s2_position, "size", 0.0) or 0.0)

228: 
229:     if not hasattr(state.s2_position, "side"):
230:         state.s2_position.side = ""
231: 
232: 
233: def _reset_to_flat(state) -> None:

234:     state.s2_position.position = "FLAT"
235:     state.s2_position.side = ""
236:     state.s2_position.size = 0.0
237:     state.s2_position.position_size = 0.0

238:     state.s2_position.entry_price = None

239:     state.s2_position.entry_timestamp_utc = ""
240: 
241: 

242: def _resolve_audit_log_path() -> str:

330:         return None
331: 
332: 
333: def _compute_duration_sec(entry_timestamp_utc: str, exit_timestamp_utc: str) -> float:
334:     dt_entry = _parse_timestamp_utc(entry_timestamp_utc)
335:     dt_exit = _parse_timestamp_utc(exit_timestamp_utc)
336: 

337:     if dt_entry is None or dt_exit is None:

338:         return 0.0
339: 
340:     duration = (dt_exit - dt_entry).total_seconds()
341:     if duration < 0:
342:         return 0.0
343:     return float(duration)

344: 

345: 
346: def _compute_pnl(side: str, entry_price: float, exit_price: float, size: float) -> float:

347:     if side == "long":
348:         return (exit_price - entry_price) * size
349:     if side == "short":

350:         return (entry_price - exit_price) * size

351:     return 0.0

352: 

353: 

354: def _compute_pnl_pct(pnl: float, entry_price: float, size: float) -> float:
355:     denom = entry_price * size
356:     if denom <= 0.0:
357:         return 0.0

358:     return pnl / denom

359: 
360: 
361: def _build_trade_id(system_state_id: str, entry_timestamp_utc: str) -> str:
362:     sid = _safe_text(system_state_id, "UNKNOWN_SYSTEM")
363:     ets = _safe_text(entry_timestamp_utc, "UNKNOWN_ENTRY_TS")
364:     return sid + "_" + ets

365: 
366: 

368:     *,
369:     state,
370:     side: str,
371:     entry_price: float,
372:     exit_price: float,
373:     entry_timestamp_utc: str,
374:     exit_timestamp_utc: str,

375:     size: float,
376:     fee_roundtrip: float,

378:     trade_log_path: Optional[str],
379: ) -> None:
380:     system_state_id = _safe_text(getattr(state, "system_state_id", ""), "")
381:     trade_id = _build_trade_id(system_state_id, entry_timestamp_utc)
382:     duration_sec = _compute_duration_sec(entry_timestamp_utc, exit_timestamp_utc)
383:     pnl_gross = _compute_pnl(side, entry_price, exit_price, size)
384:     pnl_pct_gross = _compute_pnl_pct(pnl_gross, entry_price, size)

385:     pnl_net = pnl_gross - float(fee_roundtrip)

386:     pnl_pct_net = _compute_pnl_pct(pnl_net, entry_price, size)

387: 

388:     payload = {
389:         "system_state_id": system_state_id,

390:         "trade_id": trade_id,
391:         "side": side,
392:         "entry_price": float(entry_price),
393:         "exit_price": float(exit_price),
394:         "entry_timestamp_utc": _safe_text(entry_timestamp_utc, ""),
395:         "exit_timestamp_utc": _safe_text(exit_timestamp_utc, ""),

396:         "duration_sec": float(duration_sec),
397:         "size": float(size),

398:         "pnl": float(pnl_gross),
399:         "pnl_pct": float(pnl_pct_gross),

416:     return {
417:         "position": _norm_position(getattr(state.s2_position, "position", "FLAT")),
418:         "side": _safe_text(getattr(state.s2_position, "side", ""), ""),
419:         "entry_price": _safe_optional_float(getattr(state.s2_position, "entry_price", None)),
420:         "entry_timestamp_utc": _safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),
421:         "size": _safe_float(
422:             getattr(

423:                 state.s2_position,

433:     return bool(
434:         snapshot.get("position") in ("LONG", "SHORT")
435:         and snapshot.get("side") in ("long", "short")
436:         and snapshot.get("entry_price") is not None
437:         and float(snapshot.get("entry_price")) > 0.0
438:         and float(snapshot.get("size", 0.0)) > 0.0
439:         and _safe_text(snapshot.get("entry_timestamp_utc", ""), "") != ""

440:     )

441: 
442: 

443: def _blocked_entry_decision(pos_before: str, side_after: str, entry_price, entry_timestamp_utc: str) -> ExecutionDecision:
444:     _append_audit_event({
445:         "event": "ENTRY_BLOCKED",
446:         "reason": "LOSS_CLUSTER_GATE_BLOCKED_ENTRY",

447:         "position_before": pos_before,
448:         "position_after": pos_before,
449:     })
450:     return ExecutionDecision(

451:         action="NOOP",

452:         executed=False,
453:         position_before=pos_before,
454:         position_after=pos_before,
455:         side_after=side_after,
456:         entry_price=entry_price,

457:         entry_timestamp_utc=entry_timestamp_utc,

458:         reason="LOSS_CLUSTER_GATE_BLOCKED_ENTRY",
459:     )

460: 

508: 
509:     tp_pct, sl_pct = _resolve_tp_sl_pct()
510: 
511:     entry_price_current = _safe_optional_float(getattr(state.s2_position, "entry_price", None))
512: 
513:     if pos_before == "LONG" and entry_price_current is not None and entry_price_current > 0.0:
514:         tp_price_long = entry_price_current * (1.0 + tp_pct)

515:         sl_price_long = entry_price_current * (1.0 - sl_pct)
516: 

517:         if px >= tp_price_long or px <= sl_price_long:

518:             trade_snapshot = _capture_open_position_snapshot(state)

521:                 _log_closed_trade(
522:                     state=state,
523:                     side="long",
524:                     entry_price=float(trade_snapshot["entry_price"]),
525:                     exit_price=float(px),
526:                     entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
527:                     exit_timestamp_utc=ts,

528:                     size=float(trade_snapshot["size"]),
529:                     fee_roundtrip=float(fee_roundtrip),

539:                 "timestamp_utc": ts,
540:                 "side": "long",
541:                 "price": float(px),
542:                 "position_after": "FLAT",
543:             })
544: 
545:             return ExecutionDecision(

546:                 action="CLOSE_LONG",
547:                 executed=True,
548:                 position_before="LONG",
549:                 position_after="FLAT",

550:                 side_after="",
551:                 entry_price=None,

552:                 entry_timestamp_utc="",

553:                 reason="TP_LONG_HIT" if px >= tp_price_long else "SL_LONG_HIT",
554:             )

555: 

556:     if pos_before == "SHORT" and entry_price_current is not None and entry_price_current > 0.0:
557:         tp_price_short = entry_price_current * (1.0 - tp_pct)
558:         sl_price_short = entry_price_current * (1.0 + sl_pct)
559: 

560:         if px <= tp_price_short or px >= sl_price_short:

561:             trade_snapshot = _capture_open_position_snapshot(state)

564:                 _log_closed_trade(
565:                     state=state,
566:                     side="short",
567:                     entry_price=float(trade_snapshot["entry_price"]),
568:                     exit_price=float(px),
569:                     entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
570:                     exit_timestamp_utc=ts,

571:                     size=float(trade_snapshot["size"]),
572:                     fee_roundtrip=float(fee_roundtrip),

582:                 "timestamp_utc": ts,
583:                 "side": "short",
584:                 "price": float(px),
585:                 "position_after": "FLAT",
586:             })
587: 
588:             return ExecutionDecision(

589:                 action="CLOSE_SHORT",
590:                 executed=True,
591:                 position_before="SHORT",
592:                 position_after="FLAT",

593:                 side_after="",
594:                 entry_price=None,

595:                 entry_timestamp_utc="",

596:                 reason="TP_SHORT_HIT" if px <= tp_price_short else "SL_SHORT_HIT",
597:             )

598: 

602:         trade_snapshot = _capture_open_position_snapshot(state)
603: 
604:         if _valid_trade_snapshot(trade_snapshot):
605:             duration_sec = _compute_duration_sec(
606:                 _safe_text(trade_snapshot["entry_timestamp_utc"], ""),
607:                 ts,
608:             )

609: 

610:             if duration_sec >= LONG_TIME_STOP_SEC:
611:                 _log_closed_trade(
612:                     state=state,
613:                     side="long",

614:                     entry_price=float(trade_snapshot["entry_price"]),
615:                     exit_price=float(px),
616:                     entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
617:                     exit_timestamp_utc=ts,

618:                     size=float(trade_snapshot["size"]),
619:                     fee_roundtrip=float(fee_roundtrip),

625: 
626:                 _append_audit_event({
627:                     "event": "EXIT_EXECUTED",
628:                     "reason": "LONG_TIME_STOP_HIT",
629:                     "timestamp_utc": ts,
630:                     "side": "long",
631:                     "price": float(px),

632:                     "position_after": "FLAT",
633:                 })
634: 
635:                 return ExecutionDecision(

636:                     action="CLOSE_LONG",
637:                     executed=True,
638:                     position_before=pos_before,
639:                     position_after="FLAT",

640:                     side_after="",
641:                     entry_price=None,

642:                     entry_timestamp_utc="",

643:                     reason="LONG_TIME_STOP_HIT",
644:                 )

645: 

646:     if pos_before == "SHORT":

647:         trade_snapshot = _capture_open_position_snapshot(state)
648: 
649:         if _valid_trade_snapshot(trade_snapshot):
650:             duration_sec = _compute_duration_sec(
651:                 _safe_text(trade_snapshot["entry_timestamp_utc"], ""),
652:                 ts,
653:             )

654: 

655:             if duration_sec >= SHORT_TIME_STOP_SEC:
656:                 _log_closed_trade(
657:                     state=state,
658:                     side="short",

659:                     entry_price=float(trade_snapshot["entry_price"]),
660:                     exit_price=float(px),
661:                     entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
662:                     exit_timestamp_utc=ts,

663:                     size=float(trade_snapshot["size"]),
664:                     fee_roundtrip=float(fee_roundtrip),

670: 
671:                 _append_audit_event({
672:                     "event": "EXIT_EXECUTED",
673:                     "reason": "SHORT_TIME_STOP_HIT",
674:                     "timestamp_utc": ts,
675:                     "side": "short",
676:                     "price": float(px),

677:                     "position_after": "FLAT",
678:                 })
679: 
680:                 return ExecutionDecision(

681:                     action="CLOSE_SHORT",
682:                     executed=True,
683:                     position_before=pos_before,
684:                     position_after="FLAT",

685:                     side_after="",
686:                     entry_price=None,

687:                     entry_timestamp_utc="",

688:                     reason="SHORT_TIME_STOP_HIT",
689:                 )

690: 

691:     if intent_final == "HOLD":

692:         return ExecutionDecision(
693:             action="NOOP",
694:             executed=False,
695:             position_before=pos_before,
696:             position_after=pos_before,
697:             side_after=_safe_text(getattr(state.s2_position, "side", ""), ""),
698:             entry_price=getattr(state.s2_position, "entry_price", None),

699:             entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),

700:             reason="HOLD_NO_EXECUTION",
701:         )

702: 

706:                 return _blocked_entry_decision(
707:                     pos_before="FLAT",
708:                     side_after="",
709:                     entry_price=None,
710:                     entry_timestamp_utc="",
711:                 )
712: 

713:             state.s2_position.position = "LONG"

714:             state.s2_position.side = "long"
715:             state.s2_position.size = float(size_new)
716:             state.s2_position.position_size = float(size_new)

717:             state.s2_position.entry_price = float(px)

718:             state.s2_position.entry_timestamp_utc = ts
719: 
720:             _append_audit_event({

721:                 "event": "ENTRY_ACCEPTED",

723:                 "timestamp_utc": ts,
724:                 "side": "long",
725:                 "price": float(px),
726:                 "position_before": "FLAT",
727:                 "position_after": "LONG",
728:             })
729: 

730:             return ExecutionDecision(

731:                 action="OPEN_LONG",
732:                 executed=True,
733:                 position_before="FLAT",
734:                 position_after="LONG",
735:                 side_after="long",
736:                 entry_price=float(px),

737:                 entry_timestamp_utc=ts,

738:                 reason="BUY_FROM_FLAT",
739:             )

740: 

742:             return ExecutionDecision(
743:                 action="NOOP",
744:                 executed=False,
745:                 position_before="LONG",
746:                 position_after="LONG",
747:                 side_after="long",
748:                 entry_price=getattr(state.s2_position, "entry_price", None),

749:                 entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),

750:                 reason="BUY_ALREADY_LONG",
751:             )

752: 

757:                 _log_closed_trade(
758:                     state=state,
759:                     side="short",
760:                     entry_price=float(trade_snapshot["entry_price"]),
761:                     exit_price=float(px),
762:                     entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
763:                     exit_timestamp_utc=ts,

764:                     size=float(trade_snapshot["size"]),
765:                     fee_roundtrip=float(fee_roundtrip),

766:                     exit_reason="CLOSE_SHORT",
767:                     trade_log_path=trade_log_path,
768:                 )
769: 

775:                 "timestamp_utc": ts,
776:                 "side": "short",
777:                 "price": float(px),
778:                 "position_after": "FLAT",
779:             })
780: 
781:             return ExecutionDecision(

782:                 action="CLOSE_SHORT",
783:                 executed=True,
784:                 position_before="SHORT",
785:                 position_after="FLAT",

786:                 side_after="",
787:                 entry_price=None,

788:                 entry_timestamp_utc="",

789:                 reason="BUY_CLOSES_SHORT",
790:             )

791: 

795:                 return _blocked_entry_decision(
796:                     pos_before="FLAT",
797:                     side_after="",
798:                     entry_price=None,
799:                     entry_timestamp_utc="",
800:                 )
801: 

802:             state.s2_position.position = "SHORT"

803:             state.s2_position.side = "short"
804:             state.s2_position.size = float(size_new)
805:             state.s2_position.position_size = float(size_new)

806:             state.s2_position.entry_price = float(px)

807:             state.s2_position.entry_timestamp_utc = ts
808: 
809:             _append_audit_event({

810:                 "event": "ENTRY_ACCEPTED",

812:                 "timestamp_utc": ts,
813:                 "side": "short",
814:                 "price": float(px),
815:                 "position_before": "FLAT",
816:                 "position_after": "SHORT",
817:             })
818: 

819:             return ExecutionDecision(

820:                 action="OPEN_SHORT",
821:                 executed=True,
822:                 position_before="FLAT",
823:                 position_after="SHORT",
824:                 side_after="short",
825:                 entry_price=float(px),

826:                 entry_timestamp_utc=ts,

827:                 reason="SELL_FROM_FLAT",
828:             )

829: 

831:             return ExecutionDecision(
832:                 action="NOOP",
833:                 executed=False,
834:                 position_before="SHORT",
835:                 position_after="SHORT",
836:                 side_after="short",
837:                 entry_price=getattr(state.s2_position, "entry_price", None),

838:                 entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),

839:                 reason="SELL_ALREADY_SHORT",
840:             )

841: 

846:                 _log_closed_trade(
847:                     state=state,
848:                     side="long",
849:                     entry_price=float(trade_snapshot["entry_price"]),
850:                     exit_price=float(px),
851:                     entry_timestamp_utc=_safe_text(trade_snapshot["entry_timestamp_utc"], ""),
852:                     exit_timestamp_utc=ts,

853:                     size=float(trade_snapshot["size"]),
854:                     fee_roundtrip=float(fee_roundtrip),

855:                     exit_reason="CLOSE_LONG",
856:                     trade_log_path=trade_log_path,
857:                 )
858: 

864:                 "timestamp_utc": ts,
865:                 "side": "long",
866:                 "price": float(px),
867:                 "position_after": "FLAT",
868:             })
869: 
870:             return ExecutionDecision(

871:                 action="CLOSE_LONG",
872:                 executed=True,
873:                 position_before="LONG",
874:                 position_after="FLAT",

875:                 side_after="",
876:                 entry_price=None,

877:                 entry_timestamp_utc="",

878:                 reason="SELL_CLOSES_LONG",
879:             )

880: 

881:     return ExecutionDecision(
882:         action="NOOP",
883:         executed=False,
884:         position_before=pos_before,
885:         position_after=pos_before,
886:         side_after=_safe_text(getattr(state.s2_position, "side", ""), ""),
887:         entry_price=getattr(state.s2_position, "entry_price", None),

888:         entry_timestamp_utc=_safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), ""),

889:         reason="UNKNOWN_INTENT",
890:     )


```

## live_l1/core/loop.py

exists: True

```text
145:     if recovered.position not in ("LONG", "SHORT", "FLAT"):
146:         return {"enabled": 1, "applied": 0, "reason": "invalid_recovered_position"}
147: 
148:     if recovered.position == "FLAT":
149:         state.s2_position.position = "FLAT"
150:         state.s2_position.side = ""
151:         state.s2_position.size = 0.0

152:         state.s2_position.position_size = 0.0

153:         state.s2_position.entry_price = None

154:         state.s2_position.entry_timestamp_utc = ""
155:     else:
156:         state.s2_position.position = recovered.position

157:         state.s2_position.side = recovered.side

158:         state.s2_position.entry_price = recovered.entry_price
159:         state.s2_position.entry_timestamp_utc = recovered.entry_timestamp_utc

160: 

161:         size = float(getattr(state.s2_position, "position_size", 0.0) or 0.0)

162:         if size <= 0.0:

171:         "reason": "startup_recovery_applied",
172:         "position": str(recovered.position),
173:         "side": str(recovered.side),
174:         "entry_price": "" if recovered.entry_price is None else float(recovered.entry_price),
175:         "entry_timestamp_utc": str(recovered.entry_timestamp_utc),
176:         "execution_events_read": int(recovered.execution_events_read),
177:         "loss_cluster_state_loaded": int(recovered.loss_cluster_state_loaded),

178:     }

245:         return None
246: 
247: 
248: def _lifecycle_duration_sec(entry_ts: object, current_ts: object) -> float:
249:     a = _parse_lifecycle_ts(entry_ts)
250:     b = _parse_lifecycle_ts(current_ts)
251:     if a is None or b is None:

345:     features,
346:     regime: str,
347: ) -> None:
348:     position = str(getattr(state.s2_position, "position", "FLAT")).strip().upper()
349: 
350:     if position not in ("LONG", "SHORT"):
351:         return

352: 
353:     side = position.lower()
354: 
355:     current_score = int(
356:         features.signal("rsi_signal")

384:         "tick_id",
385:         "timestamp_utc",
386:         "snapshot_id",
387:         "entry_timestamp_utc",
388:         "side",
389:         "position",
390:         "price",

418:                 "tick_id": int(tick_id),
419:                 "timestamp_utc": str(timestamp_utc),
420:                 "snapshot_id": str(snapshot_id),
421:                 "entry_timestamp_utc": str(getattr(state.s2_position, "entry_timestamp_utc", "")),
422:                 "side": side,
423:                 "position": position,
424:                 "price": float(getattr(features, "price", 0.0)),

475:         "timestamp_utc",
476:         "snapshot_id",
477:         "action",
478:         "entry_timestamp_utc",
479:         "entry_price",
480:         "side_after",
481:         "current_score",

482:         "side_aware_score",

501:                 "timestamp_utc": str(timestamp_utc),
502:                 "snapshot_id": str(snapshot_id),
503:                 "action": action,
504:                 "entry_timestamp_utc": str(getattr(exec_decision, "entry_timestamp_utc", "")),
505:                 "entry_price": "" if getattr(exec_decision, "entry_price", None) is None else float(exec_decision.entry_price),
506:                 "side_after": str(getattr(exec_decision, "side_after", "")),
507:                 "current_score": int(current_score),

508:                 "side_aware_score": int(side_aware_score),

555:     if not last_trade:
556:         return
557: 
558:     entry_ts = str(last_trade.get("entry_timestamp_utc", "")).strip()
559:     side = str(last_trade.get("side", "")).strip().lower()
560:     real_pnl = float(last_trade.get("pnl", 0.0))
561: 

562:     entry_multiplier = None

565:         reader = csv.DictReader(fh)
566:         for row in reader:
567:             if (
568:                 str(row.get("entry_timestamp_utc", "")).strip() == entry_ts
569:                 and str(row.get("side_after", "")).strip().lower() == side
570:             ):
571:                 entry_multiplier = float(row.get("entry_shadow_multiplier", 1.0))

598:         "timestamp_utc",
599:         "snapshot_id",
600:         "action",
601:         "entry_timestamp_utc",
602:         "side",
603:         "real_pnl",
604:         "entry_shadow_multiplier",

622:                 "timestamp_utc": str(timestamp_utc),
623:                 "snapshot_id": str(snapshot_id),
624:                 "action": action,
625:                 "entry_timestamp_utc": entry_ts,
626:                 "side": side,
627:                 "real_pnl": float(real_pnl),
628:                 "entry_shadow_multiplier": float(entry_multiplier),

652:     if pos not in ("LONG", "SHORT"):
653:         return
654: 
655:     side = str(getattr(state.s2_position, "side", "")).strip().lower()
656:     entry_price = _safe_float_lifecycle(getattr(state.s2_position, "entry_price", None), 0.0)
657:     size = _safe_float_lifecycle(
658:         getattr(

659:             state.s2_position,

662:         ),
663:         0.0,
664:     )
665:     entry_ts = str(getattr(state.s2_position, "entry_timestamp_utc", "")).strip()
666: 
667:     if side not in ("long", "short") or entry_price <= 0.0 or size <= 0.0 or entry_ts == "":
668:         return

669: 
670:     duration_sec = _lifecycle_duration_sec(entry_ts, timestamp_utc)

671: 
672:     if duration_sec < 60.0:
673:         return

674: 
675:     if int(duration_sec) % 60 != 0:

676:         return
677: 
678:     current_price = _safe_float_lifecycle(getattr(features, "price", 0.0), 0.0)

679:     if side == "long":
680:         unrealized_pnl = (current_price - entry_price) * size
681:     else:
682:         unrealized_pnl = (entry_price - current_price) * size

683: 

684:     out_path = os.path.join(repo_root, "live_logs", "trade_lifecycle_snapshots.csv")
685:     os.makedirs(os.path.dirname(out_path), exist_ok=True)

689:         "tick",
690:         "snapshot_id",
691:         "side",
692:         "duration_sec",
693:         "entry_timestamp_utc",
694:         "entry_price",
695:         "current_price",

696:         "position_size",

697:         "unrealized_pnl",

715:                 "tick": int(tick_id),
716:                 "snapshot_id": snapshot_id,
717:                 "side": side,
718:                 "duration_sec": float(duration_sec),
719:                 "entry_timestamp_utc": entry_ts,
720:                 "entry_price": float(entry_price),
721:                 "current_price": float(current_price),

722:                 "position_size": float(size),

723:                 "unrealized_pnl": float(unrealized_pnl),

867:             features = build_feature_snapshot(snapshot)
868:             regime = detect_regime(features)
869: 
870:             current_position = "FLAT"
871:             if hasattr(state, "s2_position") and hasattr(state.s2_position, "position"):
872:                 current_position = str(state.s2_position.position).strip().upper()
873: 

874:             intent_1m_raw, forced = compute_1m_intent_raw(
875:                 cfg=cfg,

1020:                     "tick": tick.tick_id,
1021:                     "action": exec_decision.action,
1022:                     "executed": int(exec_decision.executed),
1023:                     "position_before": exec_decision.position_before,
1024:                     "position_after": exec_decision.position_after,
1025:                     "side_after": exec_decision.side_after,
1026:                     "entry_price": "" if exec_decision.entry_price is None else float(exec_decision.entry_price),

1027:                     "entry_timestamp_utc": exec_decision.entry_timestamp_utc,

1028:                     "reason": exec_decision.reason,
1029:                 },

1030:             )

```

## live_l1/state/state_store.py

exists: True

```text
85:         symbol="BTCUSDT",
86:         position="FLAT",
87:         size=0.0,
88:         entry_price=None,
89:     )
90:     setattr(s2, "entry_timestamp_utc", "")
91:     setattr(s2, "position_size", 0.0)

92:     setattr(s2, "last_intent_id", "")
93:     setattr(s2, "snapshot_id", "")

124:         loaded_system_state_id = _safe_text(s2_last.get("system_state_id"), loaded_system_state_id)
125: 
126:         s2.symbol = _safe_text(s2_last.get("symbol"), "BTCUSDT")
127:         s2.position = _safe_text(s2_last.get("position"), "FLAT").upper()
128:         s2.size = float(_safe_float(s2_last.get("size"), 0.0) or 0.0)
129:         s2.entry_price = _safe_float(s2_last.get("entry_price"), None)
130: 

131:         setattr(s2, "entry_timestamp_utc", _safe_text(s2_last.get("entry_timestamp_utc"), ""))
132:         setattr(s2, "position_size", float(_safe_float(s2_last.get("position_size"), s2.size) or 0.0))

133:         setattr(s2, "last_intent_id", _safe_text(s2_last.get("last_intent_id"), ""))
134:         setattr(s2, "snapshot_id", _safe_text(s2_last.get("snapshot_id"), ""))

135: 
136:         loaded_side = _safe_text(s2_last.get("side"), "")
137:         if loaded_side == "":
138:             if s2.position == "LONG":
139:                 loaded_side = "long"

140:             elif s2.position == "SHORT":

141:                 loaded_side = "short"

142:         setattr(s2, "side", loaded_side)

143: 

144:     if s4_last:

178:     s4_path = os.path.join(state_dir, "s4_risk.jsonl")
179: 
180:     s2_position_size = _safe_float(getattr(state.s2_position, "position_size", getattr(state.s2_position, "size", 0.0)), 0.0)
181:     s2_entry_timestamp_utc = _safe_text(getattr(state.s2_position, "entry_timestamp_utc", ""), "")
182:     s2_last_intent_id = _safe_text(getattr(state.s2_position, "last_intent_id", ""), "")
183:     s2_snapshot_id = _safe_text(getattr(state.s2_position, "snapshot_id", ""), "")
184:     s2_side = _safe_text(getattr(state.s2_position, "side", ""), "")

185: 
186:     s4_trades_6h = _safe_int(getattr(state.s4_risk, "trades_6h", 0), 0)
187:     s4_trades_today = _safe_int(getattr(state.s4_risk, "trades_today", 0), 0)

196:             "position": state.s2_position.position,
197:             "side": s2_side,
198:             "size": state.s2_position.size,
199:             "entry_price": state.s2_position.entry_price,
200:             "entry_timestamp_utc": s2_entry_timestamp_utc,
201:             "position_size": s2_position_size,
202:             "last_intent_id": s2_last_intent_id,

203:             "snapshot_id": s2_snapshot_id,

```

## live_l1/state/models.py

exists: True

```text
18:     symbol: str
19:     position: str  # FLAT/LONG/SHORT (L1: FLAT only)
20:     size: float    # 0.0 in L1
21:     entry_price: Optional[float]
22: 
23: 
24: @dataclass

```

## Preliminary Interpretation

P28H showed repeated time-stop close events after reconstructed position was already FLAT.

P28I collects the relevant source-code areas for manual review before patching.

No code changes are introduced in this step.

## Result

Status: PASS
