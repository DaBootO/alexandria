from fastapi import FastAPI, HTTPException, Depends, Query
from contextlib import asynccontextmanager
from sqlalchemy import inspect, insert, select
from sqlalchemy import Column, Integer, String, Float, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
import sqlalchemy.dialects as dialect
from sqlalchemy_utils import database_exists, create_database

import uuid

from pydantic import BaseModel

# debug flag to show exceptions
DEBUG = True

base_uri = 'mysql+aiomysql://root:test123@localhost:3306/'
uri = 'mysql+aiomysql://root:test123@localhost:3306/experiments'

# !
# # Async engine
# engine = create_async_engine(uri)
# # inspector = Inspector(engine)
# AsyncSessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False
# )

engine = None
AsyncSessionLocal = None

# CLASSES AND NEEDED FUNCTIONS
# matching the string values from a json dict to Column types
def unwrap_col(value):
    match value.split(".")[0]:
        case "str":
            return Column(String(length=255))
        case "[str]":
            return Column(JSON(String(length=255)))
        case "int":
            return Column(Integer)
        case "float":
            return Column(Float)

# matching the string values from a json dict to Column types
def rewrap_col(value):
    match type(value):
        case dialect.mysql.types.INTEGER:
            return "int"
        case dialect.mysql.types.VARCHAR:
            return "str"
        case dialect.mysql.types.FLOAT:
            return "float"
        case dialect.mysql.types.LONGTEXT:
            return "[str]"

# Database Models
def create_table_class(table_name: str, cols: dict):
    Base = declarative_base()
    class DynamicTable(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
    
    # unwrapping the cols
    for key, value in cols.items():
        dtype = unwrap_col(value)
        setattr(DynamicTable, key, dtype)
    
    return DynamicTable

# Pydantic Models
class ExperimentCreate(BaseModel):
    cols: dict
    tags: list = []


### FUNCTIONALITIES
async def check_base_database():
    base_engine = create_async_engine(base_uri)
    async with base_engine.begin() as conn:
        db = await conn.run_sync(
            lambda check_db: database_exists(engine.url)
        )
        if db:
            return True
        else:
            print("DATABASE DOES NOT EXIST!")
            test = create_table_class(table_name='experiments')
            
            return False

async def create_database(engine, model_class):
    # Create the table for this model if it doesn't exist
    if await check_existing_table(model_class):
        async with engine.begin() as conn:
            await conn.run_sync(model_class.metadata.create_all)
    else:
        raise Exception(f'Table {model_class.__tablename__} already exists!')

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_columns_by_table_name(table_name):
    async with engine.begin() as conn:
        columns = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_columns(table_name)
        )
        return {col['name']: rewrap_col(col['type']) for col in columns if col['name'] != "id"}

async def check_existing_table(model_class):
    async with engine.begin() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
        if model_class.__tablename__ in tables:
            return True
        return False

# async def create_table_for_model(engine, model_class):
#     # Create the table for this model if it doesn't exist
#     if not await check_existing_table(model_class):
#         async with engine.begin() as conn:
#             await conn.run_sync(model_class.metadata.create_all)
#     else:
#         raise Exception(f'Table {model_class.__tablename__} already exists!')

async def create_table_for_model(engine, model_class):
    try:
        if not await check_existing_table(model_class):
            async with engine.begin() as conn:
                await conn.run_sync(model_class.metadata.create_all)
    except Exception as e:
        print(f"Error creating table: {model_class.__tablename__}, {e}")
        raise


# async def delete_table(engine, model_class):
#     # Delete a table
#     if await check_existing_table(model_class):
#         async with engine.begin() as conn:
#             await conn.run_sync(model_class.__table__.drop)
#     else:
#         raise Exception(f'Table {model_class.__tablename__} does not exist (anymore)!')

async def delete_table(engine, model_class):
    try:
        if await check_existing_table(model_class):
            async with engine.begin() as conn:
                await conn.run_sync(model_class.metadata.drop_all)
        else:
            raise Exception(f'Table {model_class.__tablename__} does not exist!')
    except Exception as e:
        print(f"Error deleting table: {model_class.__tablename__}, {e}")
        raise


### ROUTING
# context manager for startup and stop functionality
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # startup
#     if await check_base_database():
#         # create relational table if not exists
#         RelationalTable = create_table_class(table_name="__relations__", cols={"uuid": "str", "tag": "[str]"})
#         # if table does not already exist -> create
#         if not await check_existing_table(RelationalTable):
#             await create_table_for_model(engine, RelationalTable)
#         yield
#     # stop

@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    global AsyncSessionLocal
    engine = create_async_engine(uri)
    AsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    # startup
    if await check_base_database():
        # create relational table if not exists
        RelationalTable = create_table_class(table_name="__relations__", cols={"uuid": "str", "tag": "[str]"})
        # if table does not already exist -> create
        if not await check_existing_table(RelationalTable):
            await create_table_for_model(RelationalTable)
    yield
    # shutdown
    await engine.dispose()

# FastAPI App
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def get_index():
    """check if Server is running

    Returns:
        json: success message
    """
    return {"message": "Server is Running"}

# tables

@app.post("/createExperiment/")
async def create_experiment(
    experiment: ExperimentCreate,
    db: AsyncSession = Depends(get_db)
    ):
    """create_experiment

    Args:
        experiment (ExperimentCreate): json data getting passed from user
            - {"cols": {col dict}, "tags": [tag list]}
            - cols:
                - "col_name": "type"
                - types will be unwrapped to special sqlalchemy types
            - tags:
                - list of tags to be relationaly saved

        db (AsyncSession, optional): Defaults to Depends(get_db).

    Raises:
        HTTPException: if error -> return error string

    Returns:
        dict: uuid for experiment created
    """
    try:
        # generate uuid for experiment
        unique_id = uuid.uuid4()
        # Create a dynamic table class
        DynamicTable = create_table_class(table_name=unique_id, cols=experiment.cols)
        # Ensure the table is created
        await create_table_for_model(engine, DynamicTable)
        
        # read tags from request
        tags_list = experiment.tags
        tag_data = {"data": {"uuid": unique_id, "tag": tags_list}}

        await insert_data("__relations__", tag_data, db)
        # return the uuid for further inserts etc
        return {"uuid": unique_id}
    except Exception as e:
        if DEBUG:
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/deleteExperiment/{uuid}")
async def delete_experiment(
    uuid: str,
    db: AsyncSession = Depends(get_db)
    ):
    try:
        cols = await get_columns_by_table_name(uuid)
        # Create a dynamic table class
        DynamicTable = create_table_class(table_name=uuid, cols=cols)
        # delete table
        await delete_table(engine, DynamicTable)
        
        return {"message": f"deleted table with uuid = {uuid}",
                "deleted_uuid": uuid}
    except Exception as e:
        if DEBUG:
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insertData/{uuid}")
async def insert_data(
    uuid: str,
    data: dict,
    db: AsyncSession = Depends(get_db)
    ):
    """insert_data

    Args:
        table_name (str): name of the table to be inserted into (uuid)
        data (dict): data as dict from json data in request
            - {"data": {"col1": "hello", "col2": 3.141}}
            - data types have to be correct or else "type casting" will
            occur -> float to int etc.
            => maybe check?
            - if data is a list -> concat the elements
        db (AsyncSession, optional): Defaults to Depends(get_db).

    Raises:
        HTTPException: if error -> return error string

    Returns:
        dict: sucess message
    """
    try:
        # Create an instance of the dynamically created table class
        columns_dict = await get_columns_by_table_name(uuid)
        DynamicTable = create_table_class(table_name=uuid, cols=columns_dict)

        
        # Insert data into the table
        async with db as session:
        # if multiple dicts exist in a list -> concat
            if isinstance(data['data'], list):
                for data_array in data['data']:
                    stmt = insert(DynamicTable).values(**data_array)
                    await session.execute(stmt)
            else:
                stmt = insert(DynamicTable).values(**data['data'])
                await session.execute(stmt)
            await session.commit()

        return {"message": "Data inserted successfully"}
    except Exception as e:
        if DEBUG:
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/getColumns/{uuid}")
async def get_columns(
    uuid: str,
    db: AsyncSession = Depends(get_db)
    ):
    try:
        # Create an instance of the dynamically created table class
        columns_dict = await get_columns_by_table_name(uuid)
        return columns_dict
    except Exception as e:
        if DEBUG:
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/readData")
async def read_data(
    uuid: str = Query(None, title="UUID", description="The UUID parameter"),
    num: int = Query(100, title="Num", description="The num parameter (optional)"),
    start: int = Query(None, title="Start", description="The start parameter (optional)"),
    stop: int = Query(None, title="Stop", description="The stop parameter (optional)"),
    db: AsyncSession = Depends(get_db)
    ):
    try:
        # Create an instance of the dynamically created table class
        columns_dict = await get_columns_by_table_name(uuid)
        DynamicTable = create_table_class(table_name=uuid, cols=columns_dict)
        # Insert data into the table
        async with db as session:
            stmt = select(DynamicTable)
            
            if num is not None and (start is not None and stop is not None):
                stmt = stmt.where(DynamicTable.id < num)
            
            result = await session.execute(stmt)
            raw_data = result.fetchall()
            # Transform the query results into the desired JSON format
            data = [{column.name: getattr(row[0], column.name) for column in DynamicTable.__table__.columns} for row in raw_data]
            return data
    except Exception as e:
        if DEBUG:
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/getTags")
async def get_tags(
    tag: str = Query(None, title="tag", description="tag identifier (optional)"),
    db: AsyncSession = Depends(get_db)
    ):
    try:
        # Create an instance of the dynamically created table class
        table_name = "__relations__"
        columns_dict = await get_columns_by_table_name(table_name)
        DynamicTable = create_table_class(table_name=table_name, cols=columns_dict)
        # Insert data into the table
        async with db as session:
            stmt = select(DynamicTable)
            
            if tag is not None:
                tag_list = tag.split(',')
                for tag in tag_list:
                    stmt = stmt.where(DynamicTable.tag.contains(tag))
            
            result = await session.execute(stmt)
            raw_data = result.fetchall()
            # Transform the query results into the desired JSON format
            data = [{getattr(row[0], "uuid"): getattr(row[0], "tag")} for row in raw_data]
            return data
    except Exception as e:
        if DEBUG:
            raise e
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
