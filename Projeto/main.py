from fastapi import FastAPI, Depends, HTTPException, status, Cookie, Response, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional, Annotated
from sqlmodel import Session, select, SQLModel, create_engine
from contextlib import asynccontextmanager
from database import Post,Amigos, Usuario, Obra


#Criar database
arquivo_sqlite = "Projeto.db"
url_sqlite = f"sqlite:///{arquivo_sqlite}"

engine = create_engine(url_sqlite)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

@asynccontextmanager
async def initFunction(app: FastAPI):
    # Executado antes da inicialização da API
    create_db_and_tables()
    yield
    # Executado ao encerrar a API

app = FastAPI(lifespan=initFunction)

    
#Html css e javaScript
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory=["templates", "templates/Partials"])
##Variaveis Globais


#verifar se esta logado
def get_active_user(session_user: Annotated[str | None, Cookie()] = None):
    # O FastAPI busca automaticamente um cookie chamado 'session_user'
    if not session_user:
        return False
    with Session(engine) as session:
        usuario = session.exec(select(Usuario).where(Usuario.username == session_user)).first()
    if not usuario:
        return False
    
    return user

@app.get("/")
async def home(request: Request, usuario: bool |Usuario = Depends(get_active_user)):
    if user==False:
        return templates.TemplateResponse(
            request=request, 
            name="home.html", 
            context={"pagina":"/login"}
        )

    amigos=usuario.amigos
    return templates.TemplateResponse(
        request=request, 
        name="home.html", 
        context={
            "pagina":"profile.html",
            "nome": usuario.username,
            "amigos": amigos,
            "obras":obras,
            
        }
    )

@app.get("/login", response_class=HTMLResponse)
async def pagLogin(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "home.html", {"pagina": "/login"})
    return templates.TemplateResponse(request, "login.html")

@app.post("/login")
async def logar(request:Request,response: Response, username: str = Form(...),senha:str = Form(...)):
    with Session(engine) as session:
        usuario = session.exec(select(Usuario).where(Usuario.username == username,Usuario.senha==senha)).first()
        if not usuario:
             raise HTTPException(404, "Usuário não encontrado")
        response.set_cookie(key="session_user", value=username)
     
        amigos =usuario.amigos

        return templates.TemplateResponse(
        request=request, 
        name="home.html", 
        context={
            "pagina":"profile.html",
            "nome": usuario.username,
            "amigos": amigos,
            "obras":usuario.obras,
          
        }
    )
    
@app.post("/usuario", response_class=HTMLResponse)
async def criarusuario(username: str =Form(...),senha=Form(...)):
#async def criarUsuario(usuario:Usuario):
    with Session(engine) as session:
        usuario = Usuario(username=username,senha=senha)
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return HTMLResponse(content=f"<p>Usuario(a) {usuario.username} criado(a)!</p>")
    
@app.post("/obras")
async def registrarObras(obra: Obra):
    with Session(engine) as session:
        session.add(obra)
        session.commit()
        session.refresh(obra)
        return obra

@app.post("/post")
async def postar(
        username:str,
        obraNome:str,
        tipo:str,
        meta:Optional[int],
        visto: Optional[int],
        reacao:Optional[int],
        comentarios:Optional[str]
):
    with Session(engine) as session:
        obra = session.exec(select(Obra).where(Obra.nome == obraNome,Obra.tipo==tipo)).first()
        usuario = session.exec(select(Usuario).where(Usuario.username == username)).first()
        obra_id=obra.obra_id
        usuario_id=usuario.usuario_id
        post = Post(
            usuario_id=usuario_id,
            obra_id=obra_id,
            visto=visto,
            reacao=reacao,
            comentario=comentario
        )

        session.add(post)
        session.commit()

        return post

@app.patch("/post")
async def mudarPost(
        username:str,
        obraNome:str,
        tipo:str,
        visto: Optional[int],
        reacao:Optional[int],
        comentarios:Optional[str]
):
     with Session(engine) as session:
        obra = session.exec(select(Obra).where(Obra.nome == obraNome,Obra.tipo==tipo)).first()
        usuario = session.exec(select(Usuario).where(Usuario.username == username)).first()

        if not obra or not usuario:
            raise HTTPException(404, "Usuário ou obra não encontrado")
    
        query = select(Post).where(Post.usuario_id == usuario.id,
                               Post.obra_id == obra.id)
    
        post = session.exec(query).first()
    
        if not post:
             raise HTTPException(404, "Post não encontrado")
        if comentarios is not None:
             post.comentarios=comentarios
        if reacao is not None:
            post.reacao=reacao
        if visto is not None:
            post.visto=visto
        if meta is not None:
            post.meta=meta
        session.add(post)
        session.commit()
        session.refresh()
        return post

@app.delete("/post")
async def deletePost(username:str, obraNome:str, tipo:str,):
    with Session(engine) as session:
        obra = session.exec(select(Obra).where(Obra.nome == obraNome,Obra.tipo==tipo)).first()
        usuario = session.exec(select(Usuario).where(Usuario.username == username)).first()

        if not obra or not usuario:
            raise HTTPException(404, "Usuário ou obra não encontrado")
    
        query = select(Post).where(Post.usuario_id == usuario.id,
                               Post.obra_id == obra.id)
    
        post = session.exec(query).first()
    
        if not post:
            raise HTTPException(404, "Post não encontrado")
        session.delete(post)
        session.commit()
    
        return {"ok": True}


@app.delete("/usuario")
async def DeleteUsuario(username:str):
     with Session(engine) as session:
         usuario = session.exec(select(Usuario).where(Usuario.username == username)).first()
         if not usuario:
             raise HTTPException(404, "Usuário não encontrado")
         session.delete(usuario)
         session.commit()

         return {"ok": True}
