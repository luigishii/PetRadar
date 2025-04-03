from datetime import datetime
import logging
import uuid
from psycopg2.extras import RealDictCursor
from src.database.user_repository import get_user_by_email
from src.database.db_repository import connect_db

def create_pet_by_email(email: str, pet_data: dict):
    try:
        conn = connect_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Buscar o dono pelo email
        cur.execute('SELECT id FROM "user" WHERE email = %s', (email,))
        owner_data = cur.fetchone()

        if not owner_data:
            raise ValueError("Usuário não encontrado com esse e-mail")

        owner_id = owner_data["id"]

        # Buscar breed_type_id pelo nome da raça (ignorando maiúsculas/minúsculas)
        cur.execute('SELECT id FROM breed_type WHERE LOWER(name) = LOWER(%s)', (pet_data["breed_name"],))
        breed_result = cur.fetchone()

        if not breed_result:
            raise ValueError("Raça não encontrada")

        breed_type_id = breed_result["id"]

        # Buscar size_type_id pelo nome do tamanho (ignorando maiúsculas/minúsculas) ou usar um tamanho padrão
        if "size_name" in pet_data and pet_data["size_name"]:
            cur.execute('SELECT id FROM size_type WHERE LOWER(name) = LOWER(%s)', (pet_data["size_name"],))
            size_result = cur.fetchone()
            if not size_result:
                raise ValueError("Tamanho não encontrado")
            size_type_id = size_result["id"]
        else:
            # Buscar um tamanho padrão caso não seja passado
            cur.execute('SELECT id FROM size_type WHERE LOWER(name) = LOWER(%s)', ("Médio",))
            size_type_id = cur.fetchone()["id"]

        # Inserir o pet
        cur.execute(
            """
            INSERT INTO pet (id, owner_id, name, pet_type, size, health_status, found_at, created_at, breed_type_id, size_type_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), %s, %s)
            RETURNING *;
            """,
            (
                str(uuid.uuid4()), 
                str(owner_id),
                pet_data["name"],
                pet_data["pet_type"],
                pet_data["size"],
                pet_data["health_status"],
                pet_data.get("found_at"),
                str(breed_type_id),
                str(size_type_id),
            ),
        )

        new_pet = cur.fetchone()
        conn.commit()
        return new_pet

    except Exception as e:
        logging.error(f"Erro ao criar pet: {e}")
        raise

    finally:
        cur.close()
        conn.close()