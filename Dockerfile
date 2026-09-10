# Use an official Python runtime as the base image
FROM python:3.14.7-slim@sha256:cad9a2c871761c413caa6fdd6441c783451e740a48aaeba60ae62a8b53525ef6

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
CMD ["python","main.py"]
# TODO: add a EXPOSE <port>


