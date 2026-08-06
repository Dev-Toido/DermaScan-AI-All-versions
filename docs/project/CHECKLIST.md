# Launch Checklist: DermaScan AI V3

Before presenting or going live, ensure the following steps are complete:

- [x] **All tests pass**: Run `venv/bin/python tests/rigorous_tests.py` to confirm.
- [x] **Website runs locally**: Start using `cd docs && python -m http.server 8080`.
- [x] **Streamlit app runs locally**: Start using `streamlit run app.py` (ensure `./run_dermascan.sh` logic is functioning).
- [ ] **GitHub push successful**: Push local changes to the main branch on GitHub (`git push -u origin main`).
- [ ] **GitHub Pages enabled**: Enable Pages from the `docs/` folder on the main branch in repository settings.
- [ ] **Streamlit Cloud app deployed**: Deploy via `share.streamlit.io` pointing to `app.py`.
- [ ] **Poster printed**: Prepare the physical or digital poster for the presentation.
- [ ] **Pitch rehearsed**: Walk through the demo script highlighting Explainability (Grad-CAM) and Safety (Thresholding).
