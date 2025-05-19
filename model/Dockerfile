# FROM python:3.9-slim

# # Set working directory
# WORKDIR /app

# # Copy requirements and install dependencies
# COPY requirements.txt .
# #RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# # Copy app files
# COPY . .

# # Expose port for Flask
# EXPOSE 5000

# # Run the Flask app
# CMD ["python", "app.py"]


FROM python:3.9-slim

WORKDIR /app

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install CPU-only version of PyTorch explicitly
RUN pip install --no-cache-dir torch==2.2.2+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy rest of the app
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
