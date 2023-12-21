import asyncio
from aioch import Client
from fastapi import FastAPI, HTTPException, Depends


async def main():
    client = Client('localhost')
    databases = list_databases()
    print(databases)
    await create_database("test")

    await delete_database("test")
    pass

async def create_table(database_name: str, table_name: str, columns: list, engine = MergeTree(), comment: str, force = False ):
    client = Client('localhost')
    await client.execute(f"CREATE TABLE IF NOT EXISTS {database_name}.{table_name} {columns} ENGINE = {engine} COMMENT {comment}")

async def delete_table(database_name: str, table_name: str):
    client = Client('localhost')
    await client.execute(f"DROP TABLE IF EXISTS {database_name}.{table_name}")

async def list_databases() -> list:
    client = Client('localhost')
    databases = await client.execute('SHOW DATABASES')
    return databases

async def create_database(database_name: str, on_cluster = "", comment = "" ):
    #TODO: Add functionality for the on_cluster parameter
    client = Client('localhost')
    await client.execute(f"CREATE DATABASE IF NOT EXISTS {database_name} COMMENT {comment}")

async def delete_database(database_name: str):
    client = Client('localhost')
    await client.execute(f"DROP DATABASE IF EXISTS {database_name}")

if __name__ == "__main__":
    asyncio.run(main())