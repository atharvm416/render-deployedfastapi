# banquet_hall/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import database, metadata, DATABASE_URL
from routers import tenantrouter, unauthorizerouter, usersrouter, spacerouter, assetsrouter, vendorrouter, projectrouter, project_contactrouter, eventrouter, event_contactrouter, taskrouter, user_grouprouter
from sqlalchemy import create_engine

app = FastAPI(title="Banquet Hall Management API")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect DB
engine = create_engine(DATABASE_URL.replace('+asyncpg', ''), echo=True)
metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Include routers
app.include_router(tenantrouter.router)
app.include_router(usersrouter.router)
app.include_router(spacerouter.router)
app.include_router(assetsrouter.router)
app.include_router(vendorrouter.router)
app.include_router(projectrouter.router)
app.include_router(project_contactrouter.router)
app.include_router(eventrouter.router)
app.include_router(event_contactrouter.router)
app.include_router(taskrouter.router)
app.include_router(user_grouprouter.router)
app.include_router(unauthorizerouter.router)

