import asyncio
from aioch import Client
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends

from clickhouse_functions import list_databases

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
    return await {"databases": list_databases(client, like, ilike, limit, outfile, format)}

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
    return await create_database(client, db_name, cluster, engine, comment)