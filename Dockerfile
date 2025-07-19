FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY huawei_sms_to_telegram.py ./

# Copy environment file (override with your own .env when running)
COPY .env ./

# Ensure the script is executable
RUN chmod +x huawei_sms_to_telegram.py

# Default command
CMD ["./huawei_sms_to_telegram.py"]