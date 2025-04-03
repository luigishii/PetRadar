from fastapi import APIRouter, HTTPException, status
import logging

from src.models.models import UpdateUserRequest, UserCreate
from src.database.user_repository import delete_user, get_user_by_email, register_user, update_user

app = APIRouter()

@app.post("/v1/users", tags=["user"], status_code=status.HTTP_201_CREATED)
def register(data: UserCreate):
    try:
        response = register_user(data.model_dump())  # Converte Pydantic para dict
        return response
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))
    except Exception as e:
        logging.error("Unexpected error in register route: %s", str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during registration"
        )
        
        
@app.delete("/v1/users/{email}", tags=["user"])
def remove_user(email: str):
    try:
        return delete_user(email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao excluir usuário")
    
    
    
@app.put("/v1/users", tags=["user"])
def modify_user(email: str, user_data: UpdateUserRequest):
    try:
        return update_user(email, user_data.dict(exclude_none=True))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao atualizar usuário")
    

@app.get("/v1/users", tags=["user"])
def get_user(email: str):
    try:
        return get_user_by_email(email)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao buscar usuário")