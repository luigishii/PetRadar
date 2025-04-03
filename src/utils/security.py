import binascii
import os
from os import environ as env
import logging
import bcrypt
import json
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, Header, Security
from fastapi.security.api_key import APIKeyHeader
import jwt
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from psycopg2.extras import RealDictCursor
# from src.database.user_repository import find_user_by_user_id
# from src.models.models import Customer
from src.database.db_repository import connect_db
from src.models.schemas import User

db_conn = None 
api_key_header = APIKeyHeader(name='x-api-key', auto_error=True)
content_type_header = APIKeyHeader(name='content-type', auto_error=True)
customer_id_header = APIKeyHeader(name='customer-id', auto_error=True)

# async def customer_id_validator(customer_id: str = Security(customer_id_header)):
#     logging.info(f"ID do cliente recebido: {customer_id}")
#     from src.database.customer_repository import find_customer_by_id
    
#     try:
#         logging.debug("Chamando find_customer_by_id...")
#         customer_data = find_customer_by_id(customer_id)
#         logging.debug("Dados do cliente recuperados com sucesso.")

#         if not customer_data:
#             logging.error(f"Cliente não encontrado para o ID: {customer_id}")
#             raise HTTPException(status_code=403, detail="Customer not found.")

#         return customer_data
    
#     except ValueError as ve:
#         logging.error(f"Erro de valor: {str(ve)}")
#         raise HTTPException(status_code=403, detail="Invalid value provided.")
        
#     except Exception as e:
#         logging.error(f"Erro inesperado ao encontrar cliente: {str(e)}")
#         raise HTTPException(status_code=500, detail="Erro interno do servidor.")
    

   


# def is_admin(api_key: str = Security(api_key_header)):
#     """Check the api_key and returns customer info"""
#     from src.database.customer_repository import find_customer_by_api_key
#     customer = find_customer_by_api_key(
#         api_key=api_key
#     )

#     if not customer:
#         raise HTTPException(
#             status_code=HTTP_403_FORBIDDEN,
#             detail="Not authenticated."
#         )

#     if not customer.get('active'):
#         raise HTTPException(
#             status_code=HTTP_403_FORBIDDEN,
#             detail="Inactive user."
#         )

#     if not customer.get('is_admin'):
#         raise HTTPException(
#             status_code=HTTP_403_FORBIDDEN,
#             detail="Admin access required."
#         )

#     return True


def post_method_validator(content_type: str = Security(content_type_header)):
    """Check the content_type"""

    if content_type in ['application/json']:
        return True

    raise HTTPException(
        status_code=HTTP_400_BAD_REQUEST,
        detail="Content-type not allowed."
    )


# Função para encriptar uma string
def encrypt_key(customer_id: int) -> bytes:
    bit = os.urandom(8).hex()
    nonce = os.urandom(16).hex()
    combined_key = f"{bit}{customer_id}{nonce}"
    return combined_key


def decrypt_string(encrypted_string: str) -> int:
    length = len(encrypted_string)
    if length == 49:
        return int(encrypted_string[16])
    elif length == 50:
        return int(encrypted_string[16:18])
    elif length == 51:
        return int(encrypted_string[16:19])
    else:
        raise ValueError("Length of encrypted string not supported.")


# Função para gerar um token JWT
def create_access_token(data: dict):
    SECRET_KEY = env.get('SECRET_KEY')
    TOKEN_EXPIRATION = timedelta(minutes=30)
    to_encode = data.copy()

    if 'sub' not in to_encode:
        raise RuntimeError("Missing data to create token")

    to_encode['sub'] = str(to_encode['sub'])
    to_encode['exp'] = datetime.now(tz=timezone.utc) + TOKEN_EXPIRATION
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


def decode_access_token(authorization):
    SECRET_KEY = env.get('SECRET_KEY')
    token = authorization.split(" ")[1]

    logging.debug(f"Token recebido: {token}")

    payload = jwt.decode(
        token,
        SECRET_KEY,
        options={"require": ["exp", "sub"]},
        algorithms=["HS256"],
    )

    logging.debug(f"Payload decodificado: {payload}")

    return payload


def check_api_key_permission(api_key, customer_id):
    config_dir = "./assets/config"
    os.makedirs(config_dir, exist_ok=True)
    config_file = os.path.join(config_dir, "config.json")
    
    with open(config_file, 'r') as file:
        config_data = json.load(file)
        
    logging.info(config_data)
    
    registered_api_key = config_data.get(str(customer_id), {}).get("api_key")
    logging.info(config_data.get(customer_id, {})) 
    
    logging.info(registered_api_key)
    logging.debug(f"Registered API Key: {registered_api_key}")
    if api_key != registered_api_key:
        logging.warning(f"Unauthorized: Invalid API key for the customer {customer_id}. Expected: {registered_api_key}, Received: {api_key}")
        return False
    logging.debug("Authorized: Valid API key for the customer")
    return True


def get_api_key(customer_id: int):
    try:
        conn = connect_db()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("SELECT api_key FROM customers WHERE id = %s", (customer_id,))
        row = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if row:
            return row['api_key']
        else:
            raise HTTPException(status_code=404, detail="API key not found for customer")
    
    except Exception as e:
        logging.error("Failed to retrieve API key", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    


# def get_current_user(authorization: str = Header(None)) -> User:
#     """Recupera o usuário com base no token JWT"""

#     if authorization is None:
#         logging.error("Token não encontrado no cabeçalho")
#         raise HTTPException(status_code=401, detail="Token not found")

#     try:
#         # Decodifica o token JWT
#         payload = decode_access_token(authorization)

#         # Recupera o 'sub' (ID do usuário) do token
#         user_id = payload.get("sub")
#         if user_id is None:
#             logging.error("Campo 'sub' não encontrado no token")
#             raise HTTPException(status_code=401, detail="Subject not found in token")

#         # Busca o usuário no banco de dados usando o repositório (exemplo)
#         user = find_user_by_user_id(user_id)  

#         if user is None:
#             logging.error(f"Usuário com ID {user_id} não encontrado no banco de dados")
#             raise HTTPException(status_code=401, detail="User not found")

#         logging.debug(f"Usuário encontrado: {user}")

#         return user  # Retorna o objeto completo do usuário

#     except IndexError:
#         logging.error("Token inválido: deve ser passado como 'Bearer <token>'")
#         raise HTTPException(status_code=401, detail="Invalid token format")
#     except jwt.MissingRequiredClaimError:
#         logging.error("Token inválido")
#         raise HTTPException(status_code=401, detail="Invalid token")
#     except jwt.ExpiredSignatureError:
#         logging.error("Token expirado")
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except Exception as e:
#         logging.error(f"Erro no token JWT: {str(e)}")
#         raise HTTPException(status_code=401, detail="Invalid token")
    
    
def check_password(stored_hash: str, provided_password: str) -> bool:
    return bcrypt.checkpw(provided_password.encode("utf-8"), stored_hash.encode("utf-8"))
