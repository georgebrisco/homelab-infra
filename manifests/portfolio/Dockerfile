FROM python:3.11-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies without caching
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default command - can be overridden
CMD ["python", "stock_prices.py"]
