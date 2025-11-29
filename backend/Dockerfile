# Stage 1: Build Stage - Install dependencies
# Changed base image to Python 3.12
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Create a non-root user and switch to it for security
RUN adduser --disabled-password appuser
WORKDIR /home/appuser/app

# Copy only the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production Stage - Minimal image for running the app
# Changed base image to Python 3.12
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Create a non-root user and switch to it
RUN adduser --disabled-password appuser
WORKDIR /home/appuser/app
USER appuser

# Copy installed packages from the builder stage
# Note: The path reflects the Python 3.12 installation location
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy the application code
COPY ./app /home/appuser/app/app

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]