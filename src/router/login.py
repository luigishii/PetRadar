from fastapi import APIRouter, HTTPException, status
import logging

from src.models.models import LoginRequest, LoginResponse
from src.database.login_repository import loginfunc

app = APIRouter()

@app.post("/v1/login", tags=["login"], response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(data: LoginRequest):
    try:
        response = loginfunc(data)  
        return response
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(re))
    except Exception as e:
        logging.error("Unexpected error in login route: %s", str(e), exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during login")