# Use a lightweight Python base image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Set work directory
WORKDIR /app

# Install PostgreSQL development dependencies first
RUN apt-get update && apt-get install -y libpq-dev build-essential

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy entrypoint script first
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy project files
COPY . .

# Set default port and expose it
EXPOSE ${PORT}

# Use the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]