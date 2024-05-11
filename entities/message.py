from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    title: List[str]
    message: List[str]


class UpdateMessage(BaseModel):
    title: List[str] = None
    message: List[str] = None
