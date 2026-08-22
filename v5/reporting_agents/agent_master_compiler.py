import os

def compile_master_report():
    print("Master Compiler Agent initializing...")
    
    # Read the text chunks
    try:
        with open("v5/reporting_agents/outputs/literature.txt", "r") as f:
            lit_text = f.read()
    except FileNotFoundError:
        lit_text = "*(Literature data missing)*"

    try:
        with open("v5/reporting_agents/outputs/clinical.txt", "r") as f:
            clin_text = f.read()
    except FileNotFoundError:
        clin_text = "*(Clinical data missing)*"
        
    try:
        with open("v5/reports/technical_report.md", "r") as f:
            tech_text = f.read().replace("# DermaScan AI (V5) - Exhaustive Technical Report", "## Exhaustive Technical & Diagnostics Report")
    except FileNotFoundError:
        tech_text = "*(Technical metrics missing - Ensure run_all_agents.sh was executed)*"
        
    try:
        with open("v5/reports/biological_report.md", "r") as f:
            bio_text = f.read().replace("# DermaScan AI (V5) - Exhaustive Biological & Clinical Report", "## Exhaustive Biological & Demographic Report")
    except FileNotFoundError:
        bio_text = "*(Biological metrics missing - Ensure run_all_agents.sh was executed)*"

    master_content = f"""# DermaScan AI - Super Detailed Full Report Analysis
    
> **Project Scope:** Autonomous AI Diagnostic Pipeline for Dermatological Triage
> **Focus:** Resolving skin-tone bias, OOD failure, and clinical safety nets.

---

{clin_text}

---

{lit_text}

---

{tech_text}

---

{bio_text}
"""
    
    os.makedirs("docs", exist_ok=True)
    with open("docs/Super_Detailed_Full_Report.md", "w") as f:
        f.write(master_content)
    print("SUCCESS: Super Detailed Full Report generated at docs/Super_Detailed_Full_Report.md")

if __name__ == "__main__":
    compile_master_report()
