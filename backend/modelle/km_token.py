# backend/modelle/km_token.py
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Modell für Kilometer-Token-Einträge.
class TokenEintrag(BaseModel):
    token: str
    fahrer_email: EmailStr
    erstellt_am: datetime
    ist_genutzt: bool = False
