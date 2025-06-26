# Pull official base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (netcat-openbsd для alpine)
RUN apt-get update && apt-get install -y netcat-openbsd

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy project
COPY ./src /app/

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]