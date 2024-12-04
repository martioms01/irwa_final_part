# Use the official Python image
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy poetry files and install dependencies
COPY pyproject.toml poetry.lock /app/

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-dev

# Copy the app code to the container
COPY . .

# Expose the port that Flask will run on
EXPOSE 5000

# Set the command to run your Flask app
CMD ["poetry", "run", "flask", "--app", "web_app", "run", "--host", "0.0.0.0"]