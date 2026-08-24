#!/usr/bin/env python3

from __future__ import annotations

import unittest

import live_l1.tools.i7_reviewed_test_supervisor as supervisor


class ReviewedTestSupervisorTests(unittest.TestCase):
    def test_pinned_files_and_static_manifest(self) -> None:
        self.assertEqual(
            supervisor.verify_static_manifest(),
            supervisor.EXPECTED_TEST_METHODS,
        )
        self.assertEqual(
            supervisor.verify_pinned_files(),
            dict(sorted(supervisor.PINNED_FILES.items())),
        )

    def test_summary_parser_requires_exact_count_and_ok(self) -> None:
        output = b"Ran 12 tests in 0.100s\n\nOK\n"
        self.assertEqual(supervisor.parse_success(b"", output), 12)
        with self.assertRaises(supervisor.SupervisorError):
            supervisor.parse_success(b"", b"Ran 11 tests in 0.100s\n\nOK\n")
        with self.assertRaises(supervisor.SupervisorError):
            supervisor.parse_success(
                b"",
                b"Ran 12 tests in 0.100s\n\nOK (skipped=1)\n",
            )

    def test_full_supervised_run(self) -> None:
        result = supervisor.run_supervised(timeout_seconds=180.0)
        self.assertEqual(result["threat_model"], "REVIEWED_TEST_CODE")
        self.assertEqual(result["count"], 12)
        self.assertEqual(result["return_code"], 0)
        self.assertEqual(result["authority"], "ENGINEERING_EVIDENCE_ONLY")


if __name__ == "__main__":
    unittest.main()

