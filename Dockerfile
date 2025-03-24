FROM python:3.13-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "update_ip_endpoint.main:app", "--host", "0.0.0.0", "--port", "8000"]
