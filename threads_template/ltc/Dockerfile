# Use official Python slim image
FROM python:3.11-slim
#RUN echo "nameserver 8.8.8.8" > /etc/resolv.conf
# Set working directory
WORKDIR /app

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python deps + system packages
RUN pip install --no-cache-dir -r requirements.txt 

# Install Playwright browsers
RUN playwright install chromium --with-deps

# Copy your app
COPY . .

# Expose Flask port
EXPOSE 5000

# Run Flask
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]