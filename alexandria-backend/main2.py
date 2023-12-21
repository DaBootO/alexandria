from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

from contextlib import asynccontextmanager

from clickhouse_sqlalchemy import (
    Table, make_session, get_declarative_base, types, engines
)

from sqlalchemy.types import Integer, String

from sqlalchemy import create_engine, Column, MetaData
from sqlalchemy.orm import sessionmaker

import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

uri = 'clickhouse+native://localhost:9000/default'


# Async engine
engine = create_engine(uri)
logger.info(f"Engine created with URI: {uri}")
SessionLocal = make_session(engine=engine)


metadata = MetaData()

Base = get_declarative_base(metadata=metadata)

# Database Models
class Experiment(Base):
    __tablename__ = "experiments"
    __table_args__ = (
        engines.MergeTree(order_by=['id']),
    )
    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)
    name = Column('name', String)

def create_table_class(table_name: str):
    class DynamicTable(Base):
        __tablename__ = table_name
        __table_args__ = (
            engines.MergeTree(order_by=['id']),
        )
        metadata = Base.metadata

        id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)
        name = Column('name', String)

    
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
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(e)
    yield

# FastAPI App
app = FastAPI(lifespan=lifespan)


### Dependencies
async def get_db():
    yield SessionLocal

# Endpoint to create a new experiment
@app.post("/createExperiment/")
async def create_experiment(experiment: ExperimentCreate, db = Depends(get_db)):
    try:
        db_experiment_class = create_table_class(table_name=experiment.name)
        db_experiment_class.metadata.create_all(bind=engine)
        # await db_experiment.metadata.create_all(bind=engine)
        # Create an instance of the dynamic table class
        db_experiment_instance = db_experiment_class(name=experiment.name)
        db.add(db_experiment_instance)
        
        await db.commit()
        await db.refresh(db_experiment_instance)
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
