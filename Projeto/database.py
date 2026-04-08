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
    visto:str
    meta:Optional[int]=Field(default=None)
    reacao:Optional[str]
    comentarios:Optional[str]= Field(default=None)

class Seguir(SQLModel, table=True):
    seguindo_id: Optional[int] = Field(
        default=None,
        foreign_key="usuario.id",
        primary_key=True
    )
    seguindo:Optional["Usuario"]= Relationship(
        back_populates="seguidores",
        sa_relationship_kwargs={"foreign_keys":"Seguir.seguindo_id"},
    )
    
    seguidor_id: Optional[int] = Field(
        default=None,
        foreign_key="usuario.id",
        primary_key=True
    )
    seguidor:Optional["Usuario"]= Relationship(
        back_populates="seguindo",
        sa_relationship_kwargs={"foreign_keys":"Seguir.seguidor_id"},
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
    seguidores: List["Seguir"] = Relationship(
        back_populates="seguindo",
        sa_relationship_kwargs={
            "foreign_keys": "Seguir.seguindo_id",
            "lazy": "selectin",
        },
        
    )   
    seguindo: List["Seguir"] = Relationship(
        back_populates="seguidor",
        sa_relationship_kwargs={
            "foreign_keys": "Seguir.seguidor_id",
            "lazy": "selectin",
        },
    )

class Obra(SQLModel, table=True):
    id: Optional[int]= Field(default=None, primary_key=True)
    nome: str
    chave:str
    descricao: Optional[str]
    anoLancamento: Optional[int]
    tipo:str
    genero1: Optional[str]
    genero2: Optional[str]
    genero3: Optional[str]
    usuarios: List["Usuario"] = Relationship(
        back_populates="obras",
        link_model=Post,
    )


