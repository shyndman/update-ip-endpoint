# IP Update Endpoint

A FastAPI-based web server that updates IP addresses in environment files based on authenticated requests.

## Features

- Validates users against a predefined list
- Updates IP addresses in a specified .env file
- Executes a post-update script after successful updates
- Uses FastAPI for modern, async web handling

## Requirements

- Python 3.9 or higher
- uv package manager

## Installation

1. Clone the repository
2. Install dependencies using uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Unix/macOS
   # or
   .venv\Scripts\activate  # On Windows
   uv pip install -e .
   ```

## Configuration

Copy `.env.example` to `.env` and configure the following variables:

- `VALID_USERS`: Comma-separated list of valid usernames
- `ENV_FILE_PATH`: Path to the .env file to update
- `POST_UPDATE_SCRIPT`: Path to the post-update script to execute

## Usage

Start the server:
```bash
uvicorn update_ip_endpoint.main:app --host 0.0.0.0 --port 8000
```

### API Endpoint

#### GET /update

Updates the IP address for a validated user.

Headers:
- `X-Token-User-Name`: Username to validate
- `X-Forwarded-For`: Client IP address

Response:
```json
{
    "status": "success",
    "message": "Updated IP for username"
}
```

## Development

This project uses Ruff for linting and formatting. To run the linter:
```bash
ruff check .
```

To format code:
```bash
ruff format .
```
