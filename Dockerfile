FROM python:3.10-slim

# Install system dependencies for OpenCV and other ML libraries
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user (Hugging Face Spaces requirement)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements and install
COPY --chown=user v4/backend/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary source code directories
COPY --chown=user v3/ /app/v3/
COPY --chown=user v4/backend/ /app/v4/backend/

# The API needs to find v3 modules
ENV PYTHONPATH="/app/v3:/app"

# Start the FastAPI app on port 7860
CMD ["uvicorn", "v4.backend.api:app", "--host", "0.0.0.0", "--port", "7860"]
