# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt .

# Install dependencies and gunicorn for production usage
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy the application code and frontend files
COPY ./app ./app
COPY ./frontend ./frontend

# Expose the port the app runs on
EXPOSE 8000

# Run the FastAPI application using Gunicorn with Uvicorn workers for a "strong backend"
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
