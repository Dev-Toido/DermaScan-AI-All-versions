# Deployment Guide: DermaScan AI V3

Now that the local repository is prepared and the initial commit is made, follow these steps to deploy both the marketing website and the clinical Streamlit app.

## 1. Push to GitHub
If you haven't created the repository on GitHub yet:
1. Log in to your GitHub account (Dev-Toido).
2. Create a new empty repository named `DermaScan-AI-V3` (do NOT initialize it with a README, .gitignore, or license, as we've already created them locally).
3. Run the following command in your terminal to push the local repository to GitHub:
   ```bash
   git push -u origin main
   ```

## 2. Enable GitHub Pages (Marketing Website)
GitHub Pages will host the interactive marketing website directly from the `docs/` folder in your repository.
1. Go to your repository on GitHub.
2. Navigate to **Settings** > **Pages** (under the "Code and automation" section).
3. Under "Build and deployment", ensure the **Source** is set to "Deploy from a branch".
4. Under "Branch", select `main` from the dropdown, and change the folder from `/(root)` to `/docs`.
5. Click **Save**.
6. Wait 1-2 minutes for the site to build. It will be available at: `https://Dev-Toido.github.io/DermaScan-AI-V3/`

## 3. Deploy to Streamlit Cloud (Clinical App)
Streamlit Community Cloud will host the clinical application `app.py`.
1. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
2. You can click the "Deploy to Streamlit" badge in your `README.md` to pre-fill the deployment form, or do it manually:
   - **Repository**: `Dev-Toido/DermaScan-AI-V3`
   - **Branch**: `main`
   - **Main file path**: `app.py`
3. Click **Deploy!**
4. Streamlit Cloud will install the packages from `requirements.txt` and launch the app. It may take a few minutes for the initial build.

**Note:** The model file `dermascan_v3_best.keras` is relatively large (~78MB). GitHub standard repositories allow files up to 100MB, so it has been pushed normally.
