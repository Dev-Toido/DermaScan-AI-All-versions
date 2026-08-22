#!/bin/bash
# One-Click Super Pipeline: Testing -> Reporting -> Compilation

# 1. Initialize Conda for the script context
source ~/miniconda3/etc/profile.d/conda.sh
conda activate dermascan

# 2. Navigate to project root
cd "$(dirname "$0")"

echo "====================================================="
echo " PHASE 1: Executing Diagnostic & Performance Agents"
echo "====================================================="
cd v5/testing
./run_all_agents.sh
cd ../..

echo "====================================================="
echo " PHASE 2: Executing Literature & Clinical Agents"
echo "====================================================="
python v5/reporting_agents/agent_literature.py
python v5/reporting_agents/agent_clinical_application.py

echo "====================================================="
echo " PHASE 3: Executing Master Compiler Agent"
echo "====================================================="
python v5/reporting_agents/agent_master_compiler.py

echo "====================================================="
echo " ALL TASKS COMPLETE. Final report is at docs/Super_Detailed_Full_Report.md"
echo "====================================================="
