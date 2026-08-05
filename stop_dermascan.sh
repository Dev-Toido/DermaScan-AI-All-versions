#!/bin/bash
echo "Stopping DermaScan AI local servers..."

# Gracefully kill the Streamlit server
pkill -f "streamlit run app.py"
pkill -f "streamlit run app_v3.py"

# Gracefully kill the Website HTTP server
pkill -f "python -m http.server 8080"

echo "✅ All local services stopped."
echo ""
echo "To restart everything later (works offline!):"
echo "👉 App: ./run_dermascan.sh"
echo "👉 Website: cd docs && python -m http.server 8080"
