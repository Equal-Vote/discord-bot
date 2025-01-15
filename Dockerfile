# Use an official Python runtime as the base image
FROM python:3.12.2-slim@sha256:2bac43769ace90ebd3ad83e5392295e25dfc58e58543d3ab326c3330b505283d

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the application as a non-root user
RUN useradd -m appuser
USER appuser

# Specify the command to run the application
CMD ["python","star-voting.py"]
# TODO: add a EXPOSE <port>


