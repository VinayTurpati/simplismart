FROM python:3.9-slim

# Working directory
WORKDIR /app

# Copy the files and install dependencies into the container
COPY . /app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Define the command to run the application
CMD ["python3", "run.py", "--port", "5000"]
