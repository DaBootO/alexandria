import asyncio
from aioch import Client
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends

from clickhouse_functions import list_databases, create_database

app = FastAPI()
CLIENT = Client('localhost')


@app.get("/")
async def root():
    return {"message": "Server is Running"}

@app.get("/listDatabases")
async def list_databases_endpoint(
    client = None,
    like: Optional[str] = None,
    ilike: Optional[str] = None,
    limit: Optional[int] = None,
    outfile: Optional[str] = None,
    format: Optional[str] = None,
):
    if client is None:
        client = CLIENT
    databases = await list_databases(client, like, ilike, limit, outfile, format)
    if "error" in databases:
        return {"error": databases["error"]}
    elif "sucess" in databases:
        return {"sucess": databases}

@app.post("/createDatabase")
async def create_database_endpoint(
    db_name: str,
    client = None,
    cluster: Optional[str] = None,
    engine: Optional[str] = None,
    comment: Optional[str] = None,
):
    if client is None:
        client = CLIENT
    create_database_result = await create_database(client, db_name, cluster, engine, comment)
    if "error" in create_database_result:
        return {"error": create_database_result["error"]}
    elif "sucess" in create_database_result:
        return {"sucess": f"Database created: {db_name}"}