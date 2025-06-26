# Pull official base image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy bot code
COPY ./bot /app

# Set the entrypoint to run the bot
CMD ["python", "main.py"]