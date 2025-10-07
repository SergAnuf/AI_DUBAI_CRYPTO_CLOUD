# 1) Base image: same as your local Python
FROM python:3.10-slim

# 2) Prevent interactive prompts
ARG DEBIAN_FRONTEND=noninteractive

# 3) System dependencies (expand if you need geospatial libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4) Set working directory
WORKDIR /app

# 5) Copy only requirements first (better cache)
COPY requirements.txt .

# 6) Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# 7) Install dependencies
RUN pip install -r requirements.txt

# 8) Copy only required files and folders
COPY app.py .
COPY datasets ./datasets
COPY prompts ./prompts
COPY src ./src
COPY assets ./assets

# 9) Streamlit configuration (avoid CORS & telemetry issues)
ENV STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_ENABLEXsrfProtection=false \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 10) Expose port (Hugging Face Spaces uses 7860)
EXPOSE 7860

# 11) Start Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
