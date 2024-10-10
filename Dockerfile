# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /

# Copy the requirements file into the container
COPY reqs.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r reqs.txt

# Copy the rest of the application code into the container
COPY . .

# Specify the command to run the application
CMD ["python", "app.py"]