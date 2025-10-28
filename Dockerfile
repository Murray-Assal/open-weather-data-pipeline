FROM apache/airflow:3.1.1-python3.11

# Install additional Python dependencies
COPY requirements.txt .
# Install any additional Python packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt