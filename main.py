# API FOR TASKS APP
from fastapi import FastAPI
from database import db_engine
from routers import user
import models

# API
models.Base.metadata.create_all(bind=db_engine)
app = FastAPI()

app.include_router(router=user.router)
