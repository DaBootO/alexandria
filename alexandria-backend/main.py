from fastapi import FastAPI, HTTPException, Depends

import asyncio

from pydantic import BaseModel

from sqlalchemy import create_engine, Column, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from clickhouse_sqlalchemy import (
    Table, make_session, get_declarative_base, types, engines
)

uri = 'clickhouse+asynch://localhost:9000/experiments'

# Async engine
engine = create_async_engine(uri)
AsyncSessionLocal = sessionmaker(bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

session = make_session(engine)
metadata = MetaData()

Base = get_declarative_base(metadata=metadata)

# Database Models
# class Experiment(Base):
#     __tablename__ = ""
#     id = Column(types.Int32, primary_key=True, index=True)
#     name = Column(types.String)
def create_table_class(table_name: str):
    class DynamicTable(Base):
        __tablename__ = table_name
        __table_args__ = {'extend_existing': True}
        metadata = MetaData()

        id = Column(types.Int32, primary_key=True, index=True)
        name = Column(types.String)

    return DynamicTable

# Pydantic Models
class ExperimentCreate(BaseModel):
    # __tablename__ = "experiments"
    name: str

# FastAPI App
app = FastAPI()


### Dependencies
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Endpoint to create a new experiment
@app.post("/createExperiment/")
async def create_experiment(experiment: ExperimentCreate, db: AsyncSession = Depends(get_db)):
    try:
        db_experiment = create_table_class(table_name=experiment.name)
        db_experiment.metadata.create_all(bind=engine)
        db.add(db_experiment)
        await db.commit()
        await db.refresh(db_experiment)
        return db_experiment
    except Exception as e:
        # Add logging or more sophisticated error handling here
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("starting")
    uvicorn.run(app, host="0.0.0.0", port=8000)
