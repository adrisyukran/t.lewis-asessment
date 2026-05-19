"""Validation tests for Phase 6: Flask API and Orchestrator."""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Ensure the project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import app


class Phase6Tests(unittest.TestCase):
    """Tests for the Flask API and pipeline integration."""

    def setUp(self) -> None:
        """Configure the Flask test client."""
        self.client = app.test_client()
        self.client.testing = True

    def test_health_endpoint(self) -> None:
        """GET /api/health should return 200 and status ok."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "ok")

    @patch("backend.pipeline.NanoGPTClient")
    def test_analyze_endpoint(self, mock_client_cls: MagicMock) -> None:
        """POST /api/analyze with sample files should return 200 and expected keys."""
        # Configure the mock LLM client
        mock_instance = MagicMock()
        mock_instance.complete.return_value = "Cleaned sample report text."
        mock_instance.analyze_campaign.return_value = MagicMock(
            red_flag="Low ROAS",
            opportunity="Increase ad spend",
            summary="Campaign performance is below target.",
        )
        mock_client_cls.return_value = mock_instance

        report_path = PROJECT_ROOT / "data" / "sample_report.pdf"
        guidelines_path = PROJECT_ROOT / "data" / "brand_guidelines.txt"

        self.assertTrue(report_path.exists(), f"Report file not found: {report_path}")
        self.assertTrue(guidelines_path.exists(), f"Guidelines file not found: {guidelines_path}")

        with open(report_path, "rb") as report_file, open(guidelines_path, "rb") as guidelines_file:
            response = self.client.post(
                "/api/analyze",
                data={
                    "report": (report_file, report_path.name),
                    "guidelines": (guidelines_file, guidelines_path.name),
                },
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 200, f"Unexpected status: {response.status_code}")
        data = response.get_json()

        # Verify top-level keys
        self.assertIn("metrics", data)
        self.assertIn("context", data)
        self.assertIn("analysis", data)

        # Verify metrics structure
        metrics = data["metrics"]
        self.assertIn("spend", metrics)
        self.assertIn("roas", metrics)
        self.assertIn("ctr", metrics)
        self.assertIn("impressions", metrics)

        # Verify analysis structure
        analysis = data["analysis"]
        self.assertIn("red_flag", analysis)
        self.assertIn("opportunity", analysis)
        self.assertIn("summary", analysis)

        # Context should be a non-empty string
        self.assertIsInstance(data["context"], str)
        self.assertTrue(len(data["context"]) > 0)

    def test_analyze_missing_report(self) -> None:
        """POST /api/analyze without report should return 400."""
        guidelines_path = PROJECT_ROOT / "data" / "brand_guidelines.txt"
        with open(guidelines_path, "rb") as guidelines_file:
            response = self.client.post(
                "/api/analyze",
                data={"guidelines": (guidelines_file, guidelines_path.name)},
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 400)

    def test_analyze_missing_guidelines(self) -> None:
        """POST /api/analyze without guidelines should return 400."""
        report_path = PROJECT_ROOT / "data" / "sample_report.pdf"
        with open(report_path, "rb") as report_file:
            response = self.client.post(
                "/api/analyze",
                data={"report": (report_file, report_path.name)},
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
