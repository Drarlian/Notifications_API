from fastapi import APIRouter
from entities.message import Message, UpdateMessage
from datetime import datetime
from db_configuration.mongodb_atlas_configuration import *
from bson import ObjectId

"""
O APIRouter é uma classe do FastAPI que permite definir grupos de rotas em um aplicativo FastAPI de forma modular 
e organizada.

Funciona como um roteador para agrupar várias rotas relacionadas em um único objeto, facilitando a organização do 
código em diferentes arquivos e módulos.
"""
router = APIRouter()


# ADMISSIONS MESSAGES
@router.get("/message/admissions/all")
async def get_all_admissions_messages() -> list | dict:
    """
    Pega todas as mensagens de todos os tipos (candidate, admin) presente na tabela de mensagem.
    :return: Lista de objetos, onde cada objeto é uma mensagem.
    """
    try:
        results = await db.messages.find().to_list(length=None)
    except:
        return {"message": "Internal Error"}
    else:
        for result in results:
            result["_id"] = str(result["_id"])
        return results


@router.get("/message/admissions/all/{type_message}")
async def get_all_admissions_messages_by_type(type_message: str) -> list | dict:
    """
    Recebe o tipo de mensagem desejada e retorna todas as mensagens desse tipo.
    :param type_message: Tipo da mensagem desejada (candidate, admin)
    :return: Lista de objetos, onde cada objeto é uma mensagem.
    """
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


@router.get("/message/admissions/{id_message}")
async def get_admissions_message_by_id(id_message: str) -> dict:
    """
    Recebeu um id e retorna a mensagem referente a ela.
    :param id_message: Id da mensagem desejada.
    :return: Mensagem no formato de objeto.
    """
    try:
        # Convertendo a string para ObjectId
        obj_id = ObjectId(id_message)

        result = await db.messages.find_one({"_id": obj_id})
    except:
        return {"message": "Internal Error"}
    else:
        result["_id"] = str(result["_id"])
        return result


@router.post("/message/admissions/{type_message}")
async def create_admissions_message(type_message: str, message: Message) -> dict:
    """
    Cria uma mensagemm do tipo especificado.
    :param type_message: Tipo da mensagem desejada (candidate, admin)
    :param message: Objeto contendo a mensagem que vai ser criada.
    :return: Mensagem de sucesso ou fracasso da criação.
    """
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


@router.patch("/message/admissions/{id_message}")
async def update_admissions_message(id_message: str, message: UpdateMessage) -> dict:
    """
    Atualiza uma mensagem de acordo com o id informado.
    :param id_message: Id da mensagem que será alterada.
    :param message: Objeto contendo as informações (title, message) que vão ser alteradas.
    :return: Mensagem de sucesso ou fracasso da atualização.
    """
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


@router.delete("/message/admissions/{id_message}")
async def delete_admissions_message_by_id(id_message: str) -> dict:
    """
    Deleta um mensagem de acordo com o id informado.
    :param id_message: Id da mensagem que será deletada.
    :return: Mensagem de sucesso ou fracasso da deleção.
    """
    try:
        request = await db.messages.delete_one({"_id": ObjectId(id_message)})

        if request.deleted_count == 1:
            return {"message": "Mensagem removida com sucesso!"}
        else:
            return {"message": "Erro ao remover a mensagem!"}
    except:
        return {"message": "Can't delete the message"}
