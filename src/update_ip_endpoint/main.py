"""Main application module for the IP update endpoint."""
import os
import subprocess
from typing import List

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="IP Update Endpoint")


class Config(BaseModel):
    """Configuration model for environment variables."""
    VALID_USERS: List[str]
    ENV_FILE_PATH: str
    POST_UPDATE_SCRIPT: str


def get_config() -> Config:
    """Get configuration from environment variables."""
    try:
        return Config(
            VALID_USERS=os.environ["VALID_USERS"].split(","),
            ENV_FILE_PATH=os.environ["ENV_FILE_PATH"],
            POST_UPDATE_SCRIPT=os.environ["POST_UPDATE_SCRIPT"],
        )
    except KeyError as e:
        raise RuntimeError(f"Missing required environment variable: {e}") from e


def update_env_file(env_file_path: str, key: str, value: str) -> None:
    """Update or add a key-value pair in the .env file."""
    if not os.path.exists(env_file_path):
        with open(env_file_path, "w", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
        return

    with open(env_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    key_exists = False
    with open(env_file_path, "w", encoding="utf-8") as f:
        for line in lines:
            if line.startswith(f"{key}="):
                f.write(f"{key}={value}\n")
                key_exists = True
            else:
                f.write(line)
        if not key_exists:
            f.write(f"{key}={value}\n")


@app.get("/update")
async def update_ip(
    x_token_user_name: str = Header(..., alias="X-Token-User-Name"),
    client_host: str = Header(..., alias="X-Forwarded-For"),
) -> dict:
    """Update IP address for a validated user.

    Args:
        x_token_user_name: Username from X-Token-User-Name header
        client_host: Client IP address from X-Forwarded-For header

    Returns:
        dict: Response containing status and message

    Raises:
        HTTPException: If user is not valid or update fails
    """
    config = get_config()

    if x_token_user_name not in config.VALID_USERS:
        raise HTTPException(status_code=403, detail="Invalid user")

    key = f"{x_token_user_name.upper()}_IP"
    update_env_file(config.ENV_FILE_PATH, key, client_host)

    try:
        subprocess.run([config.POST_UPDATE_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute post-update script: {e}",
        ) from e

    return {"status": "success", "message": f"Updated IP for {x_token_user_name}"}
