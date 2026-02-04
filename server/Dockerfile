FROM dailyco/pipecat-base:0.1.8

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .

CMD ["python", "bot.py"]
