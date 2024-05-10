from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from datetime import datetime
from bson import ObjectId
from typing import List


# Função para Fechar a Conexão com o Banco de Dados
def close_mongo_connection():
    client.close()


app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carrega as variáveis de ambiente do arquivo .env:
load_dotenv()

# Pegando as variáveis de ambiente carregadas:
DB_USER: str = os.getenv('DB_USER')
DB_PASSWORD: str = os.getenv('DB_PASSWORD')
DB_URL: str = os.getenv('DB_URL')

MONGODB_URL: str = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}{DB_URL}"
client = AsyncIOMotorClient(MONGODB_URL)  # ->  Cria um cliente Assíncrono para se Conectar ao banco de dados MongoDB.
db = client["notifications"]  # -> Nome do Banco de Dados do Projeto.


class Message(BaseModel):
    title: List[str]
    message: List[str]


class UpdateMessage(BaseModel):
    title: List[str] = None
    message: List[str] = None


# ADMISSIONS MESSAGES
@app.get("/message/admissions/all")
async def get_all_admissions_messages():
    try:
        results = await db.messages.find().to_list(length=None)
    except:
        return {"message": "Internal Error"}
    else:
        for result in results:
            result["_id"] = str(result["_id"])
        return results


@app.get("/message/admissions/all/{type_message}")
async def get_all_admissions_messages_by_type(type_message: str):
    # type_message -> candidate | admin
    if type_message not in ['candidate', 'admin']:
        return {"message": "Type must be 'candidate' or 'admin'"}

    try:
        if type_message == 'candidate':
            results = await db.messages.find({"type": "admissions_candidate"}).to_list(length=None)
        else:  # ->  elif type_message == 'admin'
            results = await db.messages.find({"type": "admissions_admin"}).to_list(length=None)
    except:
        return {"message": "Internal Error"}
    else:
        for result in results:
            result["_id"] = str(result["_id"])
        return results


@app.get("/message/admissions/{id_message}")
async def get_admissions_message_by_id(id_message: str):
    try:
        # Convertendo a string para ObjectId
        obj_id = ObjectId(id_message)

        result = await db.messages.find_one({"_id": obj_id})
    except:
        return {"message": "Internal Error"}
    else:
        result["_id"] = str(result["_id"])
        return result


@app.post("/message/admissions/{type_message}")
async def create_admissions_message(type_message: str, message: Message):
    if type_message not in ['candidate', 'admin']:
        return {"error": "Type must be 'candidate' or 'admin'"}
    if len(message.title) != len(message.message):
        return {"error": "Numbers of titles and messages do not match"}

    try:
        tipo: str = "admissions_candidate" if type_message == "candidate" else "admissions_admin"
        await db.messages.insert_one({"type": tipo, "title": message.title, "message": message.message,
                                      "created_date": datetime.now()})
    except Exception as e:
        print(e)
        return {"message": "Can't create message"}
    else:
        return {"message": "Admissions message created"}


@app.patch("/message/admissions/{id_message}")
async def update_admissions_message(id_message: str, message: UpdateMessage):
    message = message.dict(exclude_unset=True)

    old_message = await get_admissions_message_by_id(id_message)
    if old_message["message"] == "Internal Error":
        return {"message": "Internal Error"}

    # Verificar se o novo campo title ou message tem o mesmo tamanho do antigo title/mensage
    if "title" in message.keys() and (len(message["title"]) != len(old_message["title"])):
        return {"error": "Title length does not match"}
    if "message" in message.keys() and (len(message["message"]) != len(old_message["message"])):
        return {"error": "Message length does not match"}

    try:
        request = await db.messages.update_one({"_id": ObjectId(id_message)}, {"$set": message})

        # Verifica se exatamente um documento foi modificado durante a operação de atualização: (Usamos o update_one)
        if request.modified_count == 1:
            if len(message) == 1:
                return {f"message": f"O campo {list(message.keys())[0]} foi alterado com sucesso!"}
            else:
                return {
                    f"message": f"Os campos | {' | '.join(list(message.keys()))} | foram alterados com sucesso!"}
        else:
            return {"message": "Falha ao atualizar a mensagem!"}
    except:
        return {"message": "Can't update the message"}


@app.delete("/message/admissions/{id_message}")
async def delete_admissions_message_by_id(id_message: str):
    try:
        request = await db.messages.delete_one({"_id": ObjectId(id_message)})

        if request.deleted_count == 1:
            return {"message": "Mensagem removida com sucesso!"}
        else:
            return {"message": "Erro ao remover a mensagem!"}
    except:
        return {"message": "Can't delete the message"}
