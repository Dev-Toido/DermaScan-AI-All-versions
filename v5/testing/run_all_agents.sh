#!/bin/bash
# Multi-Agent Testing Pipeline Execution Script

# Navigate to the project root regardless of where the script is called from
cd "$(dirname "$0")/../.."

echo "==========================================="
echo "Deploying Subagent 1: Model Performance & Metrics"
echo "==========================================="
python v5/testing/evaluate_all_models.py

echo "==========================================="
echo "Deploying Subagent 2: Clinical Explainability"
echo "==========================================="
python v5/testing/clinical_explainability.py

echo "==========================================="
echo "Deploying Subagent 3: Biological Variance"
echo "==========================================="
python v5/testing/biological_variance.py

echo "==========================================="
echo "Deploying Subagent 4: Reporting & Synthesis"
echo "==========================================="
python v5/reports/generate_reports.py

echo "==========================================="
echo "All Agents Completed. Reports saved to v5/reports/"
echo "==========================================="
