# DermaScan AI V3 - Marketing Website

This directory contains the standalone, static marketing website for the DermaScan AI V3 project.

## Features
- **Glassmorphism Design:** Modern aesthetic using Tailwind CSS.
- **Dynamic Content:** Text is loaded from `content.json` making it easy to update without editing HTML.
- **Animations:** Scroll animations via AOS and background particles.
- **Live Demo Link:** Connects users seamlessly to the local Streamlit application.

## How to Run
Since the website uses the `fetch()` API to load `content.json`, you must run it via a local web server (opening `index.html` directly as a file might cause CORS errors in some browsers).

1. Open a terminal in this directory.
2. Run a simple Python HTTP server:
   ```bash
   python -m http.server 8080
   ```
3. Open your browser and navigate to: `http://localhost:8080`

## Customization
- **Text:** Edit `content.json`
- **Styles:** Edit `style.css` or the Tailwind configuration in the `<head>` of `index.html`.
- **Logic:** Edit `main.js`
