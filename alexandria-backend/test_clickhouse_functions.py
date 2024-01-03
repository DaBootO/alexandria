import re
import pytest
from unittest.mock import AsyncMock, MagicMock
from clickhouse_functions import create_database

pytest_plugins = ('pytest_asyncio',)

@pytest.mark.asyncio
async def test_create_database_success():
    # Mock the ClickHouse client
    client = AsyncMock()

    # Call the create_database function with valid parameters
    result = await create_database(client, db_name="mydb", cluster="mycluster", engine="MergeTree", comment="My Database")

    # Assert that the ClickHouse client's execute method was called with the correct query
    client.execute.assert_called_once_with("CREATE DATABASE mydb ON CLUSTER mycluster ENGINE = MergeTree COMMENT 'My Database'")

    # Assert that the result is as expected
    assert result == "Database created: <result>"

@pytest.mark.asyncio
async def test_create_database_empty_name():
    # Mock the ClickHouse client
    client = AsyncMock()

    # Call the create_database function with an empty database name
    result = await create_database(client, db_name="")

    # Assert that the result is an error message indicating an empty database name
    assert result == {"error": "Database Name violated the rules. Please make sure that name can not be empty and only alphanumeric characters and underscores are used in the database name."}

@pytest.mark.asyncio
async def test_create_database_illegal_name():
    # Mock the ClickHouse client
    client = AsyncMock()

    # Call the create_database function with an illegal database name
    result = await create_database(client, db_name="my-db")

    # Assert that the result is an error message indicating an illegal database name
    assert result == {"error": "Database Name violated the rules. Please make sure that name can not be empty and only alphanumeric characters and underscores are used in the database name."}

@pytest.mark.asyncio
async def test_create_database_already_exists():
    # Mock the ClickHouse client
    client = AsyncMock()
    client.execute.side_effect = Exception("Database already exists")

    # Call the create_database function with a database name that already exists
    result = await create_database(client, db_name="mydb")

    # Assert that the result is an error message indicating that the database already exists
    assert result == {"error": "Database already exists: mydb"}
    
@pytest.mark.asyncio
async def test_create_database_internal_error():
    # Mock the ClickHouse client
    client = AsyncMock()
    client.execute.side_effect = Exception("Internal Server Error")

    # Call the create_database function and expect an internal server error
    result = await create_database(client, db_name="mydb")

    # Assert that the result is an error message indicating an internal server error
    assert result == {"error": "Internal Server Error"}