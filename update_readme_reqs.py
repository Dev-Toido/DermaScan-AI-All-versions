import os

def update_readme():
    path = "README.md"
    
    requirements_section = """
## 💻 System Requirements

### Hardware Requirements
- **GPU (Recommended):** NVIDIA GPU with at least 6GB VRAM (e.g., RTX 3060, RTX 4050, or higher) for hardware acceleration.
- **CPU (Fallback):** Multi-core processor (Intel i5/i7 or AMD Ryzen 5/7) if running CPU-only inference.
- **RAM:** 16GB Minimum (32GB recommended if training the dataset).
- **Storage:** 
  - 1GB for the application and pre-trained weights.
  - An additional 30GB of NVMe SSD storage if downloading the raw ISIC datasets for training.

### Software Dependencies
- **Operating System:** Windows 10/11 (WSL2 with Ubuntu heavily recommended) or Native Linux.
- **Environment Manager:** Miniconda or Anaconda.
- **Core Stack:** Python 3.10+, Node.js (v18+).
- **Machine Learning Backend:** TensorFlow 2.15, CUDA Toolkit 11.8.0, cuDNN 8.9.2.
- **Web Frameworks:** FastAPI (Backend), Next.js / React (Frontend).
"""
    
    with open(path, "r") as f:
        content = f.read()
    
    if "## 💻 System Requirements" not in content:
        content = content.replace("---\n\n## 📊 Comprehensive Reporting", requirements_section + "\n---\n\n## 📊 Comprehensive Reporting")
        
        with open(path, "w") as f:
            f.write(content)
        print("README updated successfully with requirements!")
    else:
        print("Requirements already in README.")

if __name__ == "__main__":
    update_readme()
