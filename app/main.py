# app/main.py
import asyncio
from fastapi import FastAPI

from app.routes.follow_routes import router as follow_router
from app.routes.traverse_bfs_routes import router as bfs_router
from app.routes.traverse_dfs_routes import router as dfs_router
from app.rabbitmq_consumer import start_consumer

app = FastAPI(
    title="Follow Service",
    version="0.1.0",
    description="Microservice responsible for follow/unfollow logic."
)

app.include_router(follow_router)
app.include_router(bfs_router)
app.include_router(dfs_router)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_consumer())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info"
    )
