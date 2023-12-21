from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager

import asyncio

from pydantic import BaseModel

from clickhouse_sqlalchemy import (
    Table, make_session, get_declarative_base, types, engines
)

from sqlalchemy import create_engine, Column, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

uri = 'clickhouse+asynch://localhost:9000/default'


# Async engine
engine = create_async_engine(uri)
logger.info(f"Engine created with URI: {uri}")
AsyncSessionLocal = sessionmaker(bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

session = make_session(engine)
metadata = MetaData()

Base = get_declarative_base(metadata=metadata)

# Database Models
class Experiment(Base):
    __tablename__ = "experiments"
    id = Column(types.Int32, primary_key=True, index=True)
    name = Column(types.String)

def create_table_class(table_name: str):
    class DynamicTable(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
        metadata = Base.metadata

        id = Column(types.Int32, primary_key=True, index=True)
        name = Column(types.String)

    
    # Bind the engine to the metadata of the dynamic table
    DynamicTable.metadata.bind = engine
    logger.info(f"Dynamic table class created for table: {table_name}")
    return DynamicTable

# Pydantic Models
class ExperimentCreate(BaseModel):
    # __tablename__ = "experiments"
    name: str

# the code before yield will be executed after startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            Base.metadata.bind = engine
            await conn.run_sync(Base.metadata.create_all)
        
    except Exception as e:
        print(e)
    yield

# FastAPI App
app = FastAPI(lifespan=lifespan)


### Dependencies
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Endpoint to create a new experiment
@app.post("/createExperiment/")
async def create_experiment(experiment: ExperimentCreate, db: AsyncSession = Depends(get_db)):
    try:
        async with db as session:
            db_experiment_class = create_table_class(table_name=experiment.name)
            async with engine.begin() as conn:
                await conn.run_sync(db_experiment_class.metadata.create_all)
            # await db_experiment.metadata.create_all(bind=engine)
            # Create an instance of the dynamic table class
            db_experiment_instance = db_experiment_class(name=experiment.name)
            db.add(db_experiment_instance)
            
            await session.commit()
            await session.refresh(db_experiment_instance)
            logger.info(f"Experiment created with name: {experiment.name}")
            return db_experiment_instance
    except Exception as e:
        # Add logging or more sophisticated error handling here
        logger.error(f"Error in create_experiment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("starting")
    uvicorn.run(app, host="0.0.0.0", port=8000)
