# PetRadar
Projeto TCC PetRadar

## **Proposta**

A proposta deste projeto é desenvolver um aplicativo inovador que auxilia proprietários de animais de estimação a localizar seus pets perdidos. Além disso, o aplicativo proporcionará uma plataforma para doações, tanto materiais quanto financeiras, e oferecerá um ambiente colaborativo para troca de dicas e suporte emocional a donos que enfrentam a perda de seus animais. A solução também tem como objetivo integrar ONGs, pet shops e veterinários, criando um ecossistema de apoio que facilita o acesso a serviços e promove o engajamento com os clientes.

1. Clone este repositório para a sua máquina local.

2. Crie um ambiente virtual Python e ative-o:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

4. Configure o arquivo `.env` com as variáveis de ambiente necessárias, incluindo a URL do banco de dados PostgreSQL. Aqui está um exemplo de `.env`:

    ```ini
    DB_NAME=PetRadar
    DB_USER=postgres
    DB_PASSWORD=postgres
    DB_HOST=127.0.0.1
    DB_PORT=5432



    ALEMBIC_ACCESS=postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

    LOG_LEVEL=INFO
    ```

5. Execute as migrações do Alembic para criar o banco de dados e as tabelas necessárias:

    ```bash
    alembic upgrade head
    ```

6. Inicie o servidor:

    Em ambiente de desenvolvimento, iniciar o servidor na porta 5000:

    ```bash
    uvicorn src.main:app --port 5000 --reload
    ```