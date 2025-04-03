import json
import logging
import os
from psycopg2.extras import RealDictCursor
from src.models.models import LoginRequest, LoginResponse
from src.database.db_repository import check_db_connection, connect_db
from src.utils.security import check_password, create_access_token, encrypt_key
import bcrypt


def loginfunc(data: LoginRequest):
    """Realiza o login do usuário com autenticação via banco de dados."""
    email = data.email
    password = data.password  

    logging.debug("Login attempt for email: %s", email)

    if not email or not password:
        logging.error("Missing email or password")
        raise ValueError("Email and password are required")

    try:
        conn = connect_db()
        logging.debug("Database connection established")
        
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM "user" WHERE email = %s', (email,))
            user = cur.fetchone()
            
            logging.debug("Database query executed")
            
            if not user:
                logging.error("Email not found: %s", email)
                raise ValueError("Email not found")

            logging.debug("User data retrieved: %s", user)

            # Verificar se 'password_hash' existe e é uma string
            password_hash = user.get("password_hash")
            if password_hash is None:
                logging.error("Password hash is None for user: %s", email)
                raise ValueError("Invalid password hash format")
            if not isinstance(password_hash, str):
                logging.error("Password hash is not a string: %s", password_hash)
                raise ValueError("Invalid password hash format")

            logging.debug("Password hash retrieved: %s", password_hash)

            # Verificar senha corretamente
            if not check_password(password_hash, password):
                logging.error("Wrong password for user: %s", user["id"])
                raise ValueError("Wrong password")

            # Verificar se o usuário é admin
            is_admin = user.get("is_admin", False)
            logging.debug("User: %s is_admin: %s", user["id"], is_admin)

            # Criar token de acesso
            token = create_access_token({"sub": str(user["id"])})
            logging.debug("Access token generated for user: %s", user["id"])

            return LoginResponse(
                status="Login successful",
                isAdmin=is_admin,
                access_token=token,
                token_type="bearer"
            )

    except ValueError as ve:
        logging.error("ValueError during login: %s", str(ve))
        raise
    except Exception as e:
        logging.error("Unexpected error during login: %s", str(e), exc_info=True)
        raise RuntimeError("An unexpected error occurred during login")