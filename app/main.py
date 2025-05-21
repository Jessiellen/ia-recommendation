from fastapi import FastAPI
from .database import engine, Base
from .routes import recommendations, users

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(recommendations.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the IA Recommendation System"}