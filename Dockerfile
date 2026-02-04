FROM dailyco/pipecat-base:latest

WORKDIR /app

# Copy requirements and install dependencies
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/*.py .
