from fastapi import FastAPI

from app.routers import x_routes
from app.routers import linkedin_routes

app = FastAPI(title="Social Media Automation API")

app.include_router(x_routes.router)
app.include_router(linkedin_routes.router)
# app.include_router(instagram_routes.router)
