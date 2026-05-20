"""Flask API for the campaign analysis pipeline."""

import os
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend.pipeline import Orchestrator

app = Flask(__name__)
CORS(app)

# Ensure a temporary directory exists for uploaded files
TEMP_DIR = Path(tempfile.gettempdir()) / "campaign_analysis"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


@app.route("/api/health", methods=["GET"])
def health_check() -> tuple:
    """Return a simple health-check response."""
    return jsonify({"status": "ok"}), 200


@app.route("/api/analyze", methods=["POST"])
def analyze() -> tuple:
    """Accept report and guidelines files, run the pipeline, and return results.

    Expects multipart/form-data with two file fields:
        - report: The campaign report (PDF or image).
        - guidelines: The brand guidelines text file.
    """
    if "report" not in request.files:
        return jsonify({"error": "Missing 'report' file in request."}), 400
    if "guidelines" not in request.files:
        return jsonify({"error": "Missing 'guidelines' file in request."}), 400

    report_file = request.files["report"]
    guidelines_file = request.files["guidelines"]

    # Save uploaded files to safe temporary paths
    report_path = TEMP_DIR / report_file.filename
    guidelines_path = TEMP_DIR / guidelines_file.filename

    report_file.save(report_path)
    guidelines_file.save(guidelines_path)

    try:
        orchestrator = Orchestrator()
        result = orchestrator.run_pipeline(str(report_path), str(guidelines_path))
    finally:
        # Clean up temporary files
        if report_path.exists():
            os.remove(report_path)
        if guidelines_path.exists():
            os.remove(guidelines_path)

    return jsonify(result), 200


if __name__ == "__main__":
    HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
    PORT = int(os.environ.get("FLASK_PORT", "5000"))
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() in ("true", "1", "yes")
    app.run(host=HOST, port=PORT, debug=DEBUG)
