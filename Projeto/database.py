from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class Post(SQLModel, table=True):
    usuario_id: Optional[int]= Field(
        default=None,
        foreign_key="usuario.id",
        primary_key=True,
    )
    obra_id: Optional[int] = Field(
        default=None,
        foreign_key="obra.id",
        primary_key=True,
    )
    visto:bool
    meta:Optional[int]
    reacao:int=0
    comentarios:Optional[str]

class Amigos(SQLModel, table=True):
    usuario_id: Optional[int] = Field(
        default=None, foreign_key="usuario.id", primary_key=True
    )
    amigo_id: Optional[int] = Field(
        default=None, foreign_key="usuario.id", primary_key=True
    )
    
    
class Usuario(SQLModel, table=True):
    id : Optional[int]= Field(
        default=None,
        primary_key=True
        )
    username : str= Field(unique=True)
    senha : str 
    bio: Optional[str]
    obras: List["Obra"] = Relationship(
        back_populates="usuarios",
        link_model=Post,
    )
    amigos: List["Usuario"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "Usuario.id==Amigos.usuario_id",
            "secondaryjoin": "Usuario.id==Amigos.amigo_id",
        },
        link_model=Amigos,
    )   


class Obra(SQLModel, table=True):
    id: Optional[int]= Field(default=None, primary_key=True)
    nome: str
    descricao: Optional[str]=None
    anoLancamento: Optional[int]=None
    tipo:str
    genero0: Optional[str]
    genero1: Optional[str]
    genero2: Optional[str]
    usuarios: List["Usuario"] = Relationship(
        back_populates="obras",
        link_model=Post,
    )
    numeroVisto:int=0
    numeroVera:int=0
    reacoes:int=0
    reacoesPositivas:int=0

