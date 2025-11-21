from fastapi import APIRouter
from funktionen.email_senden import sende_km_link

router = APIRouter()

@router.post("/sende-km-anfrage/")
def sende_anfrage(email: str):
    token = sende_km_link(email)
    return {"status": "gesendet", "token": token.token}
