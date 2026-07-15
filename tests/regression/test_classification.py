"""Tests for TD005-IU-014 (Regression Classification)."""

import unittest

from tests.regression.certification_boundary import CertificationDetermination
from tests.regression.classification import (
    ClassificationOutcome,
    ReEvaluationNotRecordedError,
    RegressionClassifier,
)
from tests.regression.comparison import ComparisonResult


CERTIFIED = CertificationDetermination(contract_id="AC-001", certified=True, boundary_rule_version="v1", category="AC")
UNCERTIFIED = CertificationDetermination(contract_id="X", certified=False, boundary_rule_version="v1", category="")
EQUIVALENT = ComparisonResult(equivalent=True, differences=[])
NON_EQUIVALENT_RESULT = ComparisonResult(equivalent=False, differences=[])


class TestRegressionClassifier(unittest.TestCase):
    def test_starts_pending(self):
        classifier = RegressionClassifier()
        self.assertEqual(classifier.state, "Pending")

    def test_upstream_failure_yields_invalid_comparison(self):
        classifier = RegressionClassifier()
        record = classifier.classify(
            reference_session_state="Captured",
            candidate_session_state="Failed",
            certification_determination=CERTIFIED,
            coverage_confident=True,
            comparison_result=None,
        )
        self.assertEqual(record.outcome, ClassificationOutcome.INVALID_COMPARISON)
        self.assertEqual(classifier.state, "Classified-Invalid-Comparison")

    def test_uncertified_contract_yields_indeterminate(self):
        classifier = RegressionClassifier()
        record = classifier.classify(
            reference_session_state="Captured",
            candidate_session_state="Captured",
            certification_determination=UNCERTIFIED,
            coverage_confident=True,
            comparison_result=EQUIVALENT,
        )
        self.assertEqual(record.outcome, ClassificationOutcome.INDETERMINATE)

    def test_low_coverage_confidence_yields_indeterminate(self):
        classifier = RegressionClassifier()
        record = classifier.classify(
            reference_session_state="Captured",
            candidate_session_state="Captured",
            certification_determination=CERTIFIED,
            coverage_confident=False,
            comparison_result=EQUIVALENT,
        )
        self.assertEqual(record.outcome, ClassificationOutcome.INDETERMINATE)

    def test_equivalent_comparison_yields_non_regression(self):
        classifier = RegressionClassifier()
        record = classifier.classify(
            reference_session_state="Captured",
            candidate_session_state="Captured",
            certification_determination=CERTIFIED,
            coverage_confident=True,
            comparison_result=EQUIVALENT,
        )
        self.assertEqual(record.outcome, ClassificationOutcome.NON_REGRESSION)

    def test_non_equivalent_comparison_yields_regression(self):
        classifier = RegressionClassifier()
        record = classifier.classify(
            reference_session_state="Captured",
            candidate_session_state="Captured",
            certification_determination=CERTIFIED,
            coverage_confident=True,
            comparison_result=NON_EQUIVALENT_RESULT,
        )
        self.assertEqual(record.outcome, ClassificationOutcome.REGRESSION)

    def test_never_computes_severity_or_disposition(self):
        classifier = RegressionClassifier()
        record = classifier.classify(
            reference_session_state="Captured",
            candidate_session_state="Captured",
            certification_determination=CERTIFIED,
            coverage_confident=True,
            comparison_result=NON_EQUIVALENT_RESULT,
        )
        self.assertFalse(hasattr(record, "severity"))
        self.assertFalse(hasattr(record, "priority"))
        self.assertFalse(hasattr(record, "disposition"))
        self.assertFalse(hasattr(record, "waiver"))

    def test_re_evaluate_without_note_raises(self):
        classifier = RegressionClassifier()
        classifier.classify(
            reference_session_state="Captured",
            candidate_session_state="Captured",
            certification_determination=UNCERTIFIED,
            coverage_confident=True,
            comparison_result=EQUIVALENT,
        )
        with self.assertRaises(ReEvaluationNotRecordedError):
            classifier.re_evaluate(
                re_evaluation_note="",
                reference_session_state="Captured",
                candidate_session_state="Captured",
                certification_determination=CERTIFIED,
                coverage_confident=True,
                comparison_result=EQUIVALENT,
            )

    def test_re_evaluate_before_any_classification_raises(self):
        classifier = RegressionClassifier()
        with self.assertRaises(ReEvaluationNotRecordedError):
            classifier.re_evaluate(
                re_evaluation_note="premature",
                reference_session_state="Captured",
                candidate_session_state="Captured",
                certification_determination=CERTIFIED,
                coverage_confident=True,
                comparison_result=EQUIVALENT,
            )

    def test_re_evaluate_with_note_reclassifies_indeterminate_to_non_regression(self):
        classifier = RegressionClassifier()
        classifier.classify(
            reference_session_state="Captured",
            candidate_session_state="Captured",
            certification_determination=UNCERTIFIED,
            coverage_confident=True,
            comparison_result=EQUIVALENT,
        )
        self.assertEqual(classifier.state, "Classified-Indeterminate")

        record = classifier.re_evaluate(
            re_evaluation_note="certification boundary newly resolved this contract",
            reference_session_state="Captured",
            candidate_session_state="Captured",
            certification_determination=CERTIFIED,
            coverage_confident=True,
            comparison_result=EQUIVALENT,
        )
        self.assertEqual(record.outcome, ClassificationOutcome.NON_REGRESSION)
        self.assertEqual(classifier.state, "Classified-Non-Regression")
        self.assertEqual(len(record.re_evaluation_notes), 1)


if __name__ == "__main__":
    unittest.main()
