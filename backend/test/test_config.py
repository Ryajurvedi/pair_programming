import pytest
import os
import json
from unittest import mock
from backend.app.config.config import (
    _load_db_config_url, 
    Settings, 
    CONFIG_FILE_PATH,
    ENVIRONMENT
)

# Mock config content for testing
MOCK_CONFIG_CONTENT = {
    "PRODUCTION": {
        "db_config": {
            "host": "prod_db_host",
            "port": 5432,
            "user": "prod_user",
            "password": "prod_password",
            "database": "prod_db"
        }
    },
    "TESTING": {
        "db_config": {
            "host": "test_db_host",
            "user": "test_user",
            "database": "test_db" # Port is missing here to test default fallback
        }
    },
    "DEVELOPMENT": {
        "db_config": {} # Empty config to test all default fallbacks
    }
}


@pytest.fixture(autouse=True)
def cleanup_env():
    """Fixture to ensure environment variables are cleaned up after each test."""
    original_env = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original_env)


# --- Tests for _load_db_config_url helper function ---

@pytest.mark.parametrize(
    "env_state, expected_host",
    [
        ("PRODUCTION", "prod_db_host"),
        ("TESTING", "test_db_host"),
    ]
)
def test_load_db_config_url_from_file(mocker, env_state, expected_host):
    """
    Tests successful database URL construction from config.json 
    for different environments.
    """
    # 1. Mock file reading
    mock_open = mocker.mock_open(read_data=json.dumps(MOCK_CONFIG_CONTENT))
    mocker.patch('builtins.open', mock_open)
    
    # 2. Set environment state for the test
    os.environ["ENV_STATE"] = env_state
    
    # Reload the ENVIRONMENT constant to pick up the change
    with mock.patch('backend.app.config.config.ENVIRONMENT', env_state):
        db_url = _load_db_config_url()
    
    assert expected_host in db_url
    assert f"postgresql://{MOCK_CONFIG_CONTENT[env_state]['db_config'].get('user')}" in db_url
    
    # Verify the correct file was opened
    mock_open.assert_called_once_with(CONFIG_FILE_PATH, 'r')


def test_load_db_config_url_with_defaults(mocker):
    """Tests loading config with missing values, relying on defaults."""
    os.environ["ENV_STATE"] = "DEVELOPMENT"
    
    # 1. Mock file reading with minimal config for the DEVELOPMENT block
    mock_open = mocker.mock_open(read_data=json.dumps(MOCK_CONFIG_CONTENT))
    mocker.patch('builtins.open', mock_open)
    
    # 2. Set environment and execute
    with mock.patch('backend.app.config.config.ENVIRONMENT', "DEVELOPMENT"):
        db_url = _load_db_config_url()
    
    # Should use all defaults: user=postgres, password=default_password, port=5432, database=collab_db
    expected_url = "postgresql://postgres:default_password@localhost:5432/collab_db"
    assert db_url == expected_url


def test_load_db_config_url_env_override():
    """Tests environment variable taking precedence over config file."""
    os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite:///./env_override.db"
    
    # The function should exit early, mocking the file is not strictly necessary but harmless.
    db_url = _load_db_config_url()
    
    assert db_url == "sqlite:///./env_override.db"


def test_load_db_config_url_file_not_found(mocker):
    """Tests the fallback to SQLite when config.json is missing."""
    # 1. Mock 'open' to raise FileNotFoundError
    mocker.patch('builtins.open', side_effect=FileNotFoundError)
    
    # 2. Mock 'print' to capture the warning
    mock_print = mocker.patch('builtins.print')
    
    # Ensure no ENV override is set
    if "SQLALCHEMY_DATABASE_URL" in os.environ:
        del os.environ["SQLALCHEMY_DATABASE_URL"]

    db_url = _load_db_config_url()
    
    assert db_url == "sqlite:///./code_collab.db"
    
    # 3. Verify warning message
    mock_print.assert_called_once_with(
        f"Warning: {CONFIG_FILE_PATH} not found. Falling back to SQLite."
    )


def test_load_db_config_url_general_error(mocker):
    """Tests the fallback to SQLite when a general exception occurs (e.g., bad JSON)."""
    os.environ["ENV_STATE"] = "PRODUCTION"
    
    # 1. Mock 'open' to return invalid JSON content
    mock_open = mocker.mock_open(read_data="This is not JSON")
    mocker.patch('builtins.open', mock_open)
    
    # 2. Mock 'print' to capture the warning
    mock_print = mocker.patch('builtins.print')
    
    # The json.load() call will raise a JSONDecodeError (subclass of Exception)
    db_url = _load_db_config_url()
    
    assert db_url == "sqlite:///./code_collab.db"
    
    # 3. Verify error message structure
    # Since the exact Exception message varies, we check the print call arguments.
    print_call = mock_print.call_args[0][0]
    assert "Error loading config for 'PRODUCTION'" in print_call
    assert "Falling back to SQLite." in print_call


# --- Tests for Settings class and model_validator ---

def test_settings_initialization_with_env_url():
    """Tests Pydantic initialization when SQLALCHEMY_DATABASE_URL is set in ENV."""
    expected_url = "sqlite:///./env_settings.db"
    os.environ["SQLALCHEMY_DATABASE_URL"] = expected_url
    
    # Initialize Settings. Pydantic reads ENV vars automatically.
    s = Settings()
    
    assert s.PROJECT_NAME == "PairProgrammingAPI"
    assert s.SQLALCHEMY_DATABASE_URL == expected_url


def test_settings_initialization_config_file_loaded(mocker):
    """Tests Pydantic initialization triggering _load_db_config_url."""
    # Ensure environment URL is NOT set
    if "SQLALCHEMY_DATABASE_URL" in os.environ:
        del os.environ["SQLALCHEMY_DATABASE_URL"]
        
    os.environ["ENV_STATE"] = "TESTING"
    
    # 1. Mock file reading
    mock_open = mocker.mock_open(read_data=json.dumps(MOCK_CONFIG_CONTENT))
    mocker.patch('builtins.open', mock_open)
    
    # 2. Mock the internal function directly for verification (optional but clearer)
    # Ensure we use the actual function if the mock above is not present
    mock_load = mocker.patch(
        'backend.app.config.config._load_db_config_url', 
        wraps=_load_db_config_url # Use wraps to call the real function but track calls
    )

    # Re-initialize the Settings class
    s = Settings()
    
    # 3. Verify the validator called the helper function
    mock_load.assert_called_once()
    
    # 4. Verify the resulting URL (it should be the TESTING one)
    assert s.SQLALCHEMY_DATABASE_URL == "postgresql://prod_user:prod_password@prod_db_host:5432/prod_db"