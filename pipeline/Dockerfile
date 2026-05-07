# Uses the official Playwright image — Chromium + all system deps pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the blocking scheduler (scrapes every SCRAPE_INTERVAL_HOURS hours)
CMD ["python", "scheduler.py"]
