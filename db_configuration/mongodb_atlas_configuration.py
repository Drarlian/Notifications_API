from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os


# Função para Fechar a Conexão com o Banco de Dados
def close_mongo_connection():
    client.close()


# Carrega as variáveis de ambiente do arquivo .env:
load_dotenv()

# Pegando as variáveis de ambiente carregadas:
DB_USER: str = os.getenv('DB_USER')
DB_PASSWORD: str = os.getenv('DB_PASSWORD')
DB_URL: str = os.getenv('DB_URL')

MONGODB_URL: str = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}{DB_URL}"
client = AsyncIOMotorClient(MONGODB_URL)  # ->  Cria um cliente Assíncrono para se Conectar ao banco de dados MongoDB.
db = client["notifications"]  # -> Nome do Banco de Dados do Projeto.
