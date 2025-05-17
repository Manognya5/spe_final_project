# Use a lightweight Python image
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your script
COPY data_pull.py .

# Command to run the script
CMD ["python", "data_pull.py"]
