from fastapi import FastAPI
from routen import token_kmstand

app = FastAPI()

app.include_router(token_kmstand.router)
