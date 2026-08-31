#!/usr/bin/env python3
from __future__ import annotations
import json
import tempfile
import unittest
from pathlib import Path
from live_l1.state.iu4_lifecycle_ledger import EMPTY_LEDGER_TIP,IU4LifecycleLedgerError,IU4LifecycleLedgerV1,authority_generation_id

class IU4LifecycleLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="iu4-ledger-")
        self.root=Path(self.tmp.name).resolve()
        self.ledger=IU4LifecycleLedgerV1(self.root)
        self.ledger.initialize()
    def tearDown(self): self.tmp.cleanup()
    def test_empty_and_self_reference_free_generation(self):
        self.assertEqual(self.ledger.view().ledger_tip,EMPTY_LEDGER_TIP)
        business={"position":"FLAT","sequence":0}
        generation=authority_generation_id(operation="LEGACY_GENESIS",source_authority_generation_id="NONE",source_authority_commit_anchor="NONE",manifest_fingerprint="m",approval_fingerprint="a",target_business_payload=business)
        self.assertTrue(generation.startswith("IU4-AUTHORITY-GENERATION-"))
        with self.assertRaises(IU4LifecycleLedgerError): authority_generation_id(operation="X",source_authority_generation_id="NONE",source_authority_commit_anchor="NONE",manifest_fingerprint="m",approval_fingerprint="a",target_business_payload={"ledger_tip":"x"})
    def test_prepare_commit_derives_separate_views(self):
        prep=self.ledger.append(record_type="LEGACY_GENESIS_PREPARE",lifecycle_event_id="P1",payload={"authority_generation_id":"G1"})
        self.assertEqual(self.ledger.view().open_authority_prepare_event_id,"P1")
        commit=self.ledger.append(record_type="LEGACY_GENESIS_COMMIT",lifecycle_event_id="C1",payload={"prepare_record_fingerprint":prep.record_fingerprint,"authority_generation_id":"G1","new_owner_epoch":1})
        view=self.ledger.view()
        self.assertEqual(view.authority_commit_anchor,commit.record_fingerprint)
        self.assertEqual(view.authority_generation_id,"G1")
        self.assertEqual(view.owner_epoch,1)
        self.assertNotEqual(view.ledger_tip,EMPTY_LEDGER_TIP)
    def test_authorization_consumption_is_exactly_once(self):
        kwargs=dict(lifecycle_event_id="A1",authorization_id="AUTH",authorization_fingerprint="f",operation="RESTART_ONLY",operator="op",startup_attempt_id="S",pre_state_fingerprint="state",pre_journal_head="head",pre_attempt_ledger_tip=EMPTY_LEDGER_TIP,source_authority_generation_id="NONE",source_authority_commit_anchor="NONE",consumption_timestamp_utc="2026-08-19T00:00:00Z")
        self.ledger.consume_restart_authorization(**kwargs)
        kwargs["lifecycle_event_id"]="A2";kwargs["pre_attempt_ledger_tip"]=self.ledger.view().ledger_tip
        with self.assertRaises(IU4LifecycleLedgerError): self.ledger.consume_restart_authorization(**kwargs)
    def test_runtime_session_requires_close_commit(self):
        self.ledger.append(record_type="RUNTIME_SESSION_OPEN",lifecycle_event_id="O",payload={"session_id":"S"})
        self.assertEqual(self.ledger.view().open_runtime_session_id,"S")
        self.ledger.append(record_type="RUNTIME_SESSION_CLOSE_PREPARE",lifecycle_event_id="P",payload={"session_id":"S"})
        self.assertEqual(self.ledger.view().open_runtime_session_id,"S")
        self.ledger.append(record_type="RUNTIME_SESSION_CLOSE_COMMIT",lifecycle_event_id="C",payload={"session_id":"S"})
        self.assertEqual(self.ledger.view().open_runtime_session_id,"")
    def test_tamper_and_sequence_gap_fail_closed(self):
        self.ledger.append(record_type="RECOVERY_MATERIALIZATION",lifecycle_event_id="R",payload={"x":1})
        path=self.root/"records"/"00000000000000000001.json"
        record=json.loads(path.read_text());record["payload"]["x"]=2
        path.write_text(json.dumps(record,sort_keys=True,separators=(",",":"))+"\n")
        with self.assertRaises(IU4LifecycleLedgerError): self.ledger.records()

if __name__=="__main__": unittest.main()
