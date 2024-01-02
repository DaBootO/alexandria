from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, inspect, insert, alias, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.reflection import Inspector
import sqlalchemy.dialects as dialect

import uuid

from pydantic import BaseModel

uri = 'mysql+aiomysql://root:test123@localhost:3306/experiments'

# Async engine
engine = create_async_engine(uri)
inspector = Inspector(engine)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base = declarative_base()

# matching the string values from a json dict to Column types
def unwrap_tag(value):
    match value.split(".")[0]:
        case "str":
            return Column(String(length=255))
        case "int":
            return Column(Integer)
        case "float":
            return Column(Float)

# matching the string values from a json dict to Column types
def rewrap_tag(value):
    match type(value):
        case dialect.mysql.types.INTEGER:
            return "int"
        case dialect.mysql.types.VARCHAR:
            return "str"
        case dialect.mysql.types.FLOAT:
            return "float"

# Database Models
def create_table_class(table_name: str, tags: dict):
    Base = declarative_base()
    class DynamicTable(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
        id = Column(Integer, primary_key=True, index=True)
    
    # unwrapping the tags
    for key, value in tags.items():
        dtype = unwrap_tag(value)
        setattr(DynamicTable, key, dtype)
    
    return DynamicTable

# Pydantic Models
class ExperimentCreate(BaseModel):
    tags: dict

# FastAPI App
app = FastAPI()

### Dependencies
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_columns_by_table_name(table_name):
    async with engine.begin() as conn:
        columns = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_columns(table_name)
        )
        return {col['name']: rewrap_tag(col['type']) for col in columns if col['name'] != "id"}

async def check_existing_table(model_class):
    async with engine.begin() as conn:
        tables = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
        if model_class.__tablename__ in tables:
            raise Exception(f'Table {model_class.__tablename__} already exists!')

async def create_table_for_model(engine, model_class):
    # Create the table for this model if it doesn't exist
    await check_existing_table(model_class)
    async with engine.begin() as conn:
        await conn.run_sync(model_class.metadata.create_all)

@app.post("/createExperiment/")
async def create_experiment(experiment: ExperimentCreate, db: AsyncSession = Depends(get_db)):
    try:
        # generate uuid for experiment
        unique_id = uuid.uuid4()
        # Create a dynamic table class
        DynamicTable = create_table_class(table_name=unique_id, tags=experiment.tags)
        # Ensure the table is created
        await create_table_for_model(engine, DynamicTable)
        
        # return the uuid for further inserts etc
        return {"uuid": unique_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insertData/{table_name}")
async def insert_data(table_name: str, data: dict, db: AsyncSession = Depends(get_db)):
    try:
        # Create an instance of the dynamically created table class
        columns_dict = await get_columns_by_table_name(table_name)
        DynamicTable = create_table_class(table_name=table_name, tags=columns_dict)

        # Insert data into the table
        async with db as session:
            stmt = insert(DynamicTable).values(**data['data'])
            await session.execute(stmt)
            await session.commit()

        return {"message": "Data inserted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("starting")
    uvicorn.run(app, host="0.0.0.0", port=8000)
