FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Debugging step: List contents of /app to verify file structure
# Look for this output in your Render build logs!
RUN ls -R /app

# Expose port
EXPOSE 8000

# Run the application, ensuring /app is in PYTHONPATH for the uvicorn command
CMD ["sh", "-c", "PYTHONPATH=/app uvicorn main:app --host 0.0.0.0 --port 8000"]