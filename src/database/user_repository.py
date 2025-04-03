import logging
import bcrypt
import uuid
from psycopg2.extras import RealDictCursor
from src.database.db_repository import connect_db
import re

def validate_phone(phone: str) -> str:
    """Valida e formata o número de telefone."""
    phone_pattern = re.compile(r"^\(\d{2}\) \d{4,5}-\d{4}$")  # Exemplo: (11) 99999-9999
    if not phone_pattern.match(phone):
        raise ValueError("Invalid phone format. Expected format: (XX) XXXXX-XXXX")
    return phone

def register_user(data: dict):
    """Cadastra um novo usuário no banco de dados."""
    name = data.get("name")
    last_name = data.get("last_name")
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    phone = data.get("phone")
    work_phone = data.get("work_phone")
    work_email = data.get("work_email")

    if not all([name, username, email, password, phone]):
        raise ValueError("Missing required fields")

    try:
        # Validar telefones antes da inserção
        phone = validate_phone(phone)
        work_phone = validate_phone(work_phone) if work_phone else None

        conn = connect_db()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Verificar se o email já está cadastrado
            cur.execute('SELECT id FROM "user" WHERE email = %s', (email,))
            if cur.fetchone():
                logging.error("Email already exists: %s", email)
                raise ValueError("Email already registered")

            # Gerar um UUID para o novo usuário
            new_user_id = str(uuid.uuid4())  # Converte para string antes de inserir

            # Hash da senha usando bcrypt
            password_encoded = password.encode('utf-8')
            hashed_password = bcrypt.hashpw(password_encoded, bcrypt.gensalt())

            # Inserir novo usuário
            cur.execute("""
                INSERT INTO "user" (id, name, last_name, username, email, password_hash, phone, work_phone, work_email, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'active', NOW())
                RETURNING id
            """, (new_user_id, name, last_name, username, email, hashed_password.decode('utf-8'), phone, work_phone, work_email))

            conn.commit()

            logging.info("User registered successfully: %s", new_user_id)

            return {
                "status": "User registered successfully",
                "user_id": new_user_id
            }

    except ValueError as ve:
        logging.error("ValueError during registration: %s", str(ve))
        raise
    except Exception as e:
        logging.error("Unexpected error during registration: %s", str(e), exc_info=True)
        raise RuntimeError("An unexpected error occurred during registration")
    
    
def delete_user(email: str):
    """Exclui um usuário do banco de dados pelo e-mail."""
    if not email:
        logging.error("Nenhum e-mail fornecido para exclusão.")
        raise ValueError("O e-mail é obrigatório para excluir um usuário.")

    try:
        conn = connect_db()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Verifica se o usuário existe
            cur.execute('SELECT id FROM "user" WHERE email = %s', (email,))
            user = cur.fetchone()

            if not user:
                logging.error("Usuário não encontrado: %s", email)
                raise ValueError("Usuário não encontrado.")

            # Exclui o usuário
            cur.execute('DELETE FROM "user" WHERE email = %s', (email,))
            conn.commit()
            logging.info("Usuário %s excluído com sucesso.", email)
            return {"status": "Usuário excluído com sucesso"}

    except ValueError as ve:
        logging.error("Erro ao excluir usuário: %s", str(ve))
        raise
    except Exception as e:
        logging.error("Erro inesperado ao excluir usuário: %s", str(e), exc_info=True)
        raise RuntimeError("Erro ao excluir usuário")
    
    
    
    
def update_user(email: str, new_data: dict):
    """Atualiza todas as informações do usuário no banco de dados pelo e-mail."""
    if not email:
        logging.error("Nenhum e-mail fornecido para atualização.")
        raise ValueError("O e-mail é obrigatório para atualizar o usuário.")

    if not new_data:
        logging.error("Nenhum dado novo fornecido para atualização.")
        raise ValueError("Os dados novos são obrigatórios.")

    try:
        conn = connect_db()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Verifica se o usuário existe pelo e-mail
            cur.execute('SELECT id FROM "user" WHERE email = %s', (email,))
            user = cur.fetchone()

            if not user:
                logging.error("Usuário não encontrado: Email %s", email)
                raise ValueError("Usuário não encontrado.")

            # Monta a query dinamicamente com os campos a serem atualizados
            set_clause = ", ".join([f"{key} = %s" for key in new_data.keys()])
            values = list(new_data.values()) + [email]

            query = f'UPDATE "user" SET {set_clause} WHERE email = %s'
            cur.execute(query, values)
            conn.commit()

            logging.info("Usuário com email %s atualizado com sucesso.", email)
            return {"status": "Usuário atualizado com sucesso"}

    except ValueError as ve:
        logging.error("Erro ao atualizar usuário: %s", str(ve))
        raise
    except Exception as e:
        logging.error("Erro inesperado ao atualizar usuário: %s", str(e), exc_info=True)
        raise RuntimeError("Erro ao atualizar usuário")
    
    
def get_user_by_email(email: str):
    """Busca um usuário no banco de dados pelo e-mail."""
    if not email:
        logging.error("Nenhum e-mail fornecido para busca.")
        raise ValueError("O e-mail é obrigatório para buscar o usuário.")

    try:
        conn = connect_db()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM "user" WHERE email = %s', (email,))
            user = cur.fetchone()

            if not user:
                logging.error("Usuário não encontrado: Email %s", email)
                raise ValueError("Usuário não encontrado.")

            logging.info("Usuário encontrado: %s", user)
            return user

    except ValueError as ve:
        logging.error("Erro ao buscar usuário: %s", str(ve))
        raise
    except Exception as e:
        logging.error("Erro inesperado ao buscar usuário: %s", str(e), exc_info=True)
        raise RuntimeError("Erro ao buscar usuário")