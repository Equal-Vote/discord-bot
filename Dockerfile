# Use an official Python runtime as the base image
FROM python:3.14.7-slim@sha256:51dafde81dbdb6ebde285137a295cf18a47ca95234fe388a343719cb97305b3d

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


