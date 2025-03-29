# Use an official Python runtime as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"


# Install dependencies using Poetry
RUN poetry install --no-root

# Expose port 5000 for the application
EXPOSE 5000

# Command to run the application
CMD ["poetry", "run", "python", "server.py"]