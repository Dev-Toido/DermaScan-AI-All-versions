# 🚀 Environment Setup & Hardware Troubleshooting Guide

This document serves as a future reference guide for configuring a Windows Subsystem for Linux (WSL) environment specifically tailored for AI training (like DermaScan AI), as well as routine system maintenance.

---

## Part 1: Initial Setup (WSL & Ubuntu for AI Training)

Follow these steps to build a fresh, isolated Linux environment inside Windows:

1. **Install WSL & Ubuntu**
   Open Windows PowerShell (Run as Administrator) and execute:
   ```powershell
   wsl --install
   ```
   *This installs the Windows Subsystem for Linux framework and the default Ubuntu distribution.*

2. **Reboot**
   Restart your computer if prompted to complete the WSL installation.

3. **Initialize the Linux Environment**
   Open the "Ubuntu" app from your Windows Start Menu. Complete the initial setup by creating a UNIX username and password.

4. **Create a Dedicated Workspace**
   Inside the Ubuntu terminal, create an organized directory for your AI projects:
   ```bash
   mkdir -p ~/ai_projects && cd ~/ai_projects
   ```

5. **Clone the Repository**
   Pull down the project files from GitHub:
   ```bash
   git clone https://github.com/Dev-Toido/DermaScan-AI-All-versions.git
   ```

6. **Navigate into the Project**
   ```bash
   cd DermaScan-AI-All-versions
   ```

7. **Create an Isolated Python Environment (Miniconda)**
   Creating a virtual environment ensures your AI package versions (like TensorFlow) do not conflict with system-level Linux packages. Because Ubuntu 24.04+ defaults to Python 3.12+, which is incompatible with TensorFlow 2.15, you MUST use Miniconda to install Python 3.11.
   
   First, install Miniconda:
   ```bash
   mkdir -p ~/miniconda3
   wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
   bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
   ~/miniconda3/bin/conda init bash
   ```
   **Restart your terminal**, then build the Python 3.11 environment named `dermascan`:
   ```bash
   conda create -n dermascan python=3.11 -y
   ```
   Activate the environment:
   ```bash
   conda activate dermascan
   ```
   *(Your terminal prompt will now display `(dermascan)` at the very beginning).*

8. **Install Project Dependencies (Crucial for AI)**
   With the environment activated, install the required AI libraries:
   ```bash
   pip install -r requirements.txt
   ```

---

## Part 2: Resuming Work (Connecting Antigravity IDE to WSL)

When you return to your project on another day, follow these steps to securely hook your Windows IDE into the Linux filesystem.

**Step 1: Locate your WSL Project Path**
WSL files are completely isolated inside Linux, but Windows maps them to a secure network share pathway. 
Open your WSL-Ubuntu terminal and navigate to your repository:
```bash
cd ~/ai_projects/DermaScan-AI-All-versions
```
Run the Explorer trigger command to reveal this directory directly to Windows:
```bash
explorer.exe .
```
*(Note the period `.` at the end—this tells Explorer to open the current directory).*
A Windows File Explorer window will pop up. Click the Address Bar at the top of that window and copy the path string. It will look exactly like this:
`\\wsl.localhost\Ubuntu\home\YOUR_LINUX_USERNAME\ai_projects\DermaScan-AI-All-versions`

**Step 2: Open the Folder in Google Antigravity IDE**
Launch Google Antigravity IDE on your Windows desktop. 
Click **File → Open Folder...** from the top menu bar (or use `Ctrl + K` then `Ctrl + O`). Paste the network path (`\\wsl.localhost\Ubuntu\...`) you copied from Step 1 into the folder address bar and press Enter. Click **Select Folder**. Your cloned GitHub repository files will load into the left sidebar.

**Step 3: Connect Antigravity's Terminal to WSL**
Because your Python virtual environment (`dermascan`) and AI tools are installed on the Linux layer, you need to route Antigravity's integrated terminal panel to use WSL instead of Windows PowerShell. 
1. Go to **Terminal → New Terminal** in Antigravity. 
2. If it drops you into a Windows prompt, look at the top-right corner of the terminal sub-pane and click the drop-down arrow next to the `+` icon. 
3. Select **Ubuntu (WSL)** to change the shell environment. 
4. Activate your environment inside this Antigravity terminal pane:
   ```bash
   conda activate dermascan
   ```

---

## Part 3: System Health & Clearing Junk

If your Windows host machine starts acting sluggish, throwing weird blue screens, or failing to pass hardware (GPU) connections through to WSL, run these powerful native Windows repair tools. 

Open **Windows PowerShell as Administrator** and run these strictly in order:

1. **DISM (Deployment Image Servicing and Management)**
   ```powershell
   DISM.exe /Online /Cleanup-Image /RestoreHealth
   ```
   *What it does: Scans your Windows component store for deep systemic corruption and automatically downloads healthy replacement files directly from Microsoft's Windows Update servers.*

2. **SFC (System File Checker)**
   ```powershell
   sfc /scannow
   ```
   *What it does: Checks all protected operating system files and replaces any damaged or missing files with the verified local cached copies downloaded by DISM.*

### (Optional) Clearing WSL RAM Junk
Sometimes WSL consumes too much of your Windows RAM. To force Linux to drop its cached memory junk without restarting your PC, run this inside your Ubuntu terminal:
```bash
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
```
