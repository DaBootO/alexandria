import re
import asyncio
import logging
from aioch import Client
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


async def main():
    client = Client('localhost')
    databases = await list_databases(client)
    print(databases)
    # await delete_database("test")
    # pass

async def delete_database(
    client,
    db_name: str = None,
    cluster: Optional[str] = None,
    sync: Optional[bool] = None,
):
    try:
        # Create a ClickHouse client
        ch_client = client

        # Build the DROP DATABASE query based on the provided parameters
        query = f"DROP DATABASE {db_name}"
        if cluster:
            query += f" ON CLUSTER {cluster}"
        if sync:
            query += f" SYNC"

        # Execute the query
        result = await ch_client.execute(query)

        # Log the result (this is just an example, adjust as needed)
        logging.info(f"Database deleted: {result}")

        return result
    except Exception as e:
        # Log the error
        logging.error(f"Error deleting database: {e}")
        # Return an appropriate error response if needed
        return {"error": f"Error deleting database: {e}"}
    

async def create_database(
    client,
    db_name: str = None,
    cluster: Optional[str] = None,
    engine: Optional[str] = None,
    comment: Optional[str] = None,
):
    # Check if the database name is legal
    try:
        if db_name == None or db_name.strip() == "":
            raise ValueError("Database name cannot be empty")

        if not re.match(r'^\w+$', db_name):
            raise ValueError(f"Illegal database name: {db_name}")
    except ValueError as e:
        # Log the error
        logging.error(f"Error creating database: {e}")
        # Return an appropriate error response if needed
        return {"error": "Database Name violated the rules. Please make sure that name can not be empty and only alphanumeric characters and underscores are used in the database name."}

    try:
        # Create a ClickHouse client
        ch_client = client

        # Build the CREATE DATABASE query based on the provided parameters
        query = f"CREATE DATABASE {db_name}"
        if cluster:
            query += f" ON CLUSTER {cluster}"
        if engine:
            query += f" ENGINE = {engine}"
        if comment:
            query += f" COMMENT '{comment}'"

        # Execute the query
        result = await ch_client.execute(query)

        # Log the result (this is just an example, adjust as needed)
        logging.info(f"Database created: {result}")

        return result
    except Exception as e:
        if 'already exists' in str(e):
            logging.error(f"Database already exists: {db_name}")
            return {"error": f"Database already exists: {db_name}"}
        else:
            # Log the error
            logging.error(f"Error creating database: {e}")
            # Return an appropriate error response if needed
            return {"error": "Internal Server Error"}

async def list_databases(
    client,
    like: Optional[str] = None,
    ilike: Optional[str] = None,
    limit: Optional[int] = None,
    outfile: Optional[str] = None,
    format: Optional[str] = None,
):
    try:
        # Create a ClickHouse client
        ch_client = client

        # Build the SHOW DATABASES query based on the provided parameters
        query = "SHOW DATABASES"
        if like:
            query += f" LIKE '{like}'"
        elif ilike:
            query += f" ILIKE '{ilike}'"
        if limit:
            query += f" LIMIT {limit}"

        # Execute the query
        result = await ch_client.execute(query)

        # Log the result (this is just an example, adjust as needed)
        logging.info(f"List of databases: {result}")

        return result

    except Exception as e:
        # Log the error
        logging.error(f"Error listing databases: {e}")
        # Return an appropriate error response if needed
        return {"error": "Internal Server Error"}


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    a = asyncio.run(main())