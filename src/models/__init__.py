# Importar todos os modelos para que eles registrem suas tabelas com o SQLAlchemy
from .base import Base
from .schemas import *

# Coletar todos os metadados
metadata = Base.metadata