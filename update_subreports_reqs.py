import os

def append_to_reports():
    reports = [
        "v5/reports/biological_report.md",
        "v5/reports/technical_report.md"
    ]
    
    requirements_section = """
## System Requirements & Dependencies

The DermaScan AI (V5) architecture relies on the following hardware and software stack to process the 25GB dataset and execute complex Dual-Head inferencing:

### Hardware Dependencies
- **GPU (Recommended):** NVIDIA GPU with at least 6GB VRAM (e.g., RTX 3060, RTX 4050, or higher) for hardware acceleration (CUDA/cuDNN).
- **CPU (Fallback):** Multi-core processor (Intel i5/i7 or AMD Ryzen 5/7).
- **RAM:** 32GB RAM recommended for data loading (16GB minimum).
- **Storage:** NVMe SSD strongly recommended for fast I/O throughput (requires ~30GB total).

### Software Dependencies
- **Operating System:** Windows 10/11 (WSL2 with Ubuntu heavily recommended) or Native Linux.
- **Environment Manager:** Miniconda or Anaconda.
- **Deep Learning Backend:** TensorFlow 2.15.0, CUDA Toolkit 11.8.0, cuDNN 8.9.2.
- **Backend/Frontend:** Python 3.10+, Node.js (v18+), FastAPI, Next.js.
"""
    
    for path in reports:
        if os.path.exists(path):
            with open(path, "r") as f:
                content = f.read()
            
            if "## System Requirements & Dependencies" not in content:
                with open(path, "a") as f:
                    f.write("\n---\n" + requirements_section)
                print(f"Updated {path} successfully!")
            else:
                print(f"Requirements already in {path}.")
        else:
            print(f"File {path} not found.")

if __name__ == "__main__":
    append_to_reports()
