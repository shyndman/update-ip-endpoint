"""Test script for the IP update endpoint."""
import os
import subprocess
import tempfile
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from update_ip_endpoint.main import app

# Test configuration
TEST_USER = "testuser"
TEST_IP = "192.168.1.1"
INVALID_USER = "invaliduser"

@pytest.fixture(scope="session")
def test_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir

@pytest.fixture
def test_env(test_dir):
    """Set up test environment variables."""
    env_file = Path(test_dir) / "test.env"
    post_update_script = Path(test_dir) / "post-update.sh"

    os.environ["VALID_USERS"] = TEST_USER
    os.environ["ENV_FILE_PATH"] = str(env_file)
    os.environ["POST_UPDATE_SCRIPT"] = str(post_update_script)

    yield env_file, post_update_script

@pytest.fixture
def post_update_script(test_env):
    """Create a test post-update script."""
    _, script_path = test_env
    script_content = f"""#!/bin/bash
echo "Post-update script executed" > {script_path.parent}/post_update.log
"""
    script_path.write_text(script_content)
    script_path.chmod(0o755)
    return script_path

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

def test_update_ip_success(client, test_env, post_update_script):
    """Test successful IP update."""
    env_file, _ = test_env

    response = client.get(
        "/update",
        headers={
            "X-Token-User-Name": TEST_USER,
            "X-Forwarded-For": TEST_IP,
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": f"Updated IP for {TEST_USER}",
    }

    # Verify .env file was updated
    assert env_file.exists()
    env_content = env_file.read_text()
    assert f"{TEST_USER.upper()}_IP={TEST_IP}" in env_content

    # Verify post-update script was executed
    time.sleep(0.1)  # Give time for script to execute
    log_file = Path(post_update_script).parent / "post_update.log"
    assert log_file.exists()
    assert log_file.read_text().strip() == "Post-update script executed"

def test_update_ip_invalid_user(client, test_env):
    """Test IP update with invalid user."""
    response = client.get(
        "/update",
        headers={
            "X-Token-User-Name": INVALID_USER,
            "X-Forwarded-For": TEST_IP,
        },
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid user"}

def test_update_ip_missing_headers(client, test_env):
    """Test IP update with missing headers."""
    response = client.get("/update")
    assert response.status_code == 422  # FastAPI validation error

def test_update_ip_invalid_script(client, test_env):
    """Test IP update with invalid post-update script."""
    # Create an invalid script
    _, script_path = test_env
    script_path.write_text("#!/bin/bash\nexit 1")
    script_path.chmod(0o755)

    response = client.get(
        "/update",
        headers={
            "X-Token-User-Name": TEST_USER,
            "X-Forwarded-For": TEST_IP,
        },
    )
    assert response.status_code == 500
    assert "Failed to execute post-update script" in response.json()["detail"]
