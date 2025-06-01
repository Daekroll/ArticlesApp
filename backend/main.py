from fastapi import FastAPI
import uvicorn

from api.v1.endpoints.articles import router as articles_router
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.comments import router as comments_router
from api.v1.endpoints.users import router as users_router
from core.settings import HOST, PORT
from db.session import create_db


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Startapp")
#     await create_db()
#     yield


app = FastAPI()
app.include_router(articles_router)
app.include_router(auth_router)
app.include_router(comments_router)
app.include_router(users_router)


@app.get('/')
async def root():
    return {'message':'Welcome to the Articles Root'}


if __name__ == '__main__':
    uvicorn.run('main:app', host=HOST, port=PORT, reload=True)