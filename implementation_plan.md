# Goal: Clean Up and Restructure Project Root

The project root currently contains a mix of V3, V4, and V5 files, along with various scripts from old deployments. To make the project clean, focused on V5, and to preserve our historical progress files, we will restructure the directory.

---

> [!IMPORTANT]
> ## User Review Required
> Please review the proposed folder structure below. This is a non-destructive cleanup (no files will be permanently deleted; old files will be safely archived into `legacy_history/`).
> **If you approve this plan, click Proceed and I will execute the moves.**

---

## 1. Proposed File Movements

We will create a new folder called `legacy_history/` to safely preserve all previous iterations of DermaScan without cluttering the root.

### Files/Folders to Move to `legacy_history/`:
- `v2_archive/` (Old V2 code)
- `v3/` (Old Streamlit code)
- `v4/` (Old FastAPI/NextJS code)
- `Friend's repo/` (Old unused repo)
- `.streamlit/` (V3 specific configs)
- `run_dermascan.sh`, `run_v4.sh`, `stop_dermascan.sh` (Old run scripts)
- `DermaScan_V3.desktop` (Old desktop shortcut)
- `Dockerfile`, `render.yaml` (Old deployment configs)
- `V4_Detailed_Report.md` (Old V4 report)

### Progress Files to Surface to Root:
To ensure the progress history is "outside and accessible" as requested, I will explicitly copy the AI-generated planning files from the hidden IDE folder into the actual project root so you can always see them in your file explorer:
- `implementation_plan.md` (The V5 architecture plan)
- `task.md` (The active V5 execution checklist)

*Note: `progress_log.md` is already safely in the root.*

---

## 2. The New Clean Project Structure

After the restructuring, your project root will look incredibly clean and focused:

```text
DermaScan-AI-All-versions/
├── .github/                 # Active CI/CD Workflows
├── archive/                 # Destination for your massive datasets
├── demo_images/             # Sample testing data
├── docs/                    # Active documentation
├── legacy_history/          # ALL V2, V3, and V4 history preserved safely inside here
├── logs/                    # Active system logs
├── scripts/                 # Active utilities
├── tests/                   # Active testing suite
├── v5/                      # ACTIVE WORKSPACE: The new V5 Clinical Architecture
├── .gitignore               
├── implementation_plan.md   # Progress File: V5 Architecture Plan
├── LICENSE                  
├── progress_log.md          # Progress File: Historical Log
├── README.md                
├── requirements.txt         # V5 Dependencies (Moved from v5/ to root for standard access)
└── task.md                  # Progress File: V5 Task Checklist
```

## 3. Execution Plan
1. Create the `legacy_history/` folder.
2. Move all identified legacy files and folders into it.
3. Copy `implementation_plan.md` and `task.md` from the AI brain into the root.
4. Move `v5/requirements.txt` to the root (Standard Python convention).
