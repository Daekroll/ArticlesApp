from fastapi import FastAPI
import uvicorn
app = FastAPI()

from api.v1.endpoints.articles import router as articles_router

app.include_router(articles_router)

@app.get('/')
async def root():
    return {'message':'Welcome to the Articles Root'}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)