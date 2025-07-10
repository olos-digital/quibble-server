from fastapi import FastAPI
from app.routers import linkedin_routes

app = FastAPI(title="Social Media Automation API")

app.include_router(linkedin_routes.router)