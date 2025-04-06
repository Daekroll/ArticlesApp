from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from backend.core.security import host, port
from backend.db.session import create_db



# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Startapp")
#     await create_db()
#     yield

app = FastAPI()

from backend.api.v1.endpoints.articles import router as articles_router
from backend.api.v1.endpoints.auth import router as auth_router
from backend.api.v1.endpoints.comments import router as comments_router
from backend.api.v1.endpoints.users import router as users_router

app.include_router(articles_router)
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(users_router)

@app.get('/')
async def root():
    return {'message':'Welcome to the Articles Root'}

if __name__ == '__main__':
    uvicorn.run('main:app', host=host, port=port, reload=True)