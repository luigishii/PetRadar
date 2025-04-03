from fastapi import APIRouter, HTTPException
from src.database.pet_repository import create_pet_by_email
from src.models.models import CreatePetRequest
from uuid import UUID

app = APIRouter()

@app.post("/v1/pets", tags=["pet"])
def register_pet(email: str, pet_data: CreatePetRequest):
    """Cria um pet vinculado ao dono identificado pelo e-mail."""
    try:
        return create_pet_by_email(email, pet_data.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao criar pet")
