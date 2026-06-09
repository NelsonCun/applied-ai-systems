from pydantic import BaseModel
from typing import List, Optional


class DiagnosticoRequest(BaseModel):
    sintomas: List[str]
    telegram_chat_id: Optional[str] = None


class DiagnosticoResponse(BaseModel):
    falla: str
    falla_texto: str
    recomendacion: str
    coincidencias: int
    sintomas: List[str]
    telegram_enviado: bool
