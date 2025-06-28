# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Expose the port Flask runs on
EXPOSE 5001

# Set environment variable for Flask
ENV FLASK_APP=main.py

# Run the Flask app
CMD ["python", "main.py"] 