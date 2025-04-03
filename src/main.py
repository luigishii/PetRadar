from collections import defaultdict
from datetime import datetime
import json
import logging
import os
import time
from fastapi import FastAPI, Request, HTTPException
from starlette.middleware.cors import CORSMiddleware

#project
from src.router.login import app as login_app
from src.router.users import app as users_app


# Logging setup
def setup_logging():
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file = os.path.join(log_directory, f'{datetime.now().strftime("%Y-%m-%d")}.log')
    log_level = os.environ.get('LOG_LEVEL')

    logging.basicConfig(
        filename=log_file,
        level=log_level or logging.DEBUG,
        format='[%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(funcName)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

setup_logging()

# Initialize FastAPI app
app = FastAPI()


# CORS settings
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# # Include routers
app.include_router(login_app)
app.include_router(users_app)


# Defina o limite máximo de solicitações por IP e o período de tempo em segundos
REQUEST_LIMIT = 100
TIME_PERIOD = 60

# Crie um dicionário para rastrear as contagens de solicitações por IP
request_count = defaultdict(lambda: {"count": 0, "timestamp": 0})

log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Load logging configuration from JSON file
config_path = 'log_config/logging_config.json'
    
if os.path.exists(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
else:
    with open('log_config/default_config.json', 'r') as f:
        config = json.load(f)

current_date = datetime.now().strftime("%Y-%m-%d")

log_level = os.getenv('LOG_LEVEL', 'INFO').upper()

for handler in config['handlers'].values():
    if 'filename' in handler:
        base_filename = handler['filename'].replace('%DATE%', current_date) 
        handler['filename'] = f"{os.path.splitext(base_filename)[0]}{os.path.splitext(base_filename)[1]}"
    if 'level' in handler:
        handler['level'] = log_level
             
logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

# Middleware para limitação de taxa de solicitações
@app.middleware("http")
def rate_limit_middleware(request: Request, call_next):
    blacklist = set([]) 
    client_ip = request.client.host

    if client_ip in blacklist:
        raise HTTPException(status_code=403, detail="IP bloqueado")

    data = request_count[client_ip]
    count = data["count"]
    timestamp = data["timestamp"]

    current_time = time.time()
    if timestamp < current_time - TIME_PERIOD:
        data["count"] = 1
        data["timestamp"] = current_time
    else:
        if count >= REQUEST_LIMIT:
            raise HTTPException(status_code=429, detail="Limite de solicitações excedido")
        else:
            data["count"] += 1

    response = call_next(request)
    return response

@app.get("/docs")
def get_openapi_json():
    return app.openapi()

@app.get("/v1/status", tags=["status"])
def status():
    try:
        return {"Status": "Operational"}
    except Exception as e:
        logging.error("An error occurred during health check: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred during health check")