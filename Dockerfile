FROM python:3.11-slim

# Install Chromium and dependencies
# We use chromium instead of google-chrome-stable because it supports ARM64 (Apple Silicon)
# and is available in the default Debian repositories.
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Copy requirements (if any) or create them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for user data and screenshots
RUN mkdir -p userdata debug_screenshots

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Default command
# Copy entrypoint script
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Default command
ENTRYPOINT ["./entrypoint.sh"]
CMD ["python", "class_checker.py"]
