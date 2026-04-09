from fastapi import FastAPI, Depends, HTTPException, status, Cookie, Response, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Optional, Annotated
from sqlmodel import Session, select, SQLModel, create_engine, func
from contextlib import asynccontextmanager
from database import Post,Seguir, Usuario, Obra


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
        return [False," "]
    with Session(engine) as session:
        usuario = session.exec(select(Usuario).where(Usuario.username == session_user)).first()
        if not usuario:
            return [False," "]
    
        return [True,usuario.username]

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
            request=request, 
            name="home.html", 
            context={
                "pagina":"/perfil",
            }
        )
   

@app.get("/login", response_class=HTMLResponse)
async def pagLogin(
        request: Request,
        temUsuario: [bool,str] = Depends(get_active_user)
):

    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(
            request,
            "home.html",
            {"pagina": "/login"})
    if temUsuario[0]==False:
        return templates.TemplateResponse(request, "login.html")
    return templates.TemplateResponse(request, "profile.html")
@app.post("/login")
async def logar(
        request:Request,
        response: Response,
        username: str = Form(...),
        senha:str = Form(...)
):
    with Session(engine) as session:
        usuario = session.exec(select(Usuario).where(Usuario.username == username,Usuario.senha==senha)).first()
        if not usuario:
             raise HTTPException(404, "Usuário não encontrado")
        response.set_cookie(key="session_user", value=username)
        return {"message": "Logado com sucesso"}

@app.get("/perfil", response_class=HTMLResponse)
async def perfil(request: Request, temUsuario: [bool,str] = Depends(get_active_user)):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(
            request,
            "home.html",
            {"pagina": "/perfil"}
        )
    with Session(engine) as session:
        usuario = session.exec(select(Usuario).where(Usuario.username == temUsuario[1])).first()
        if temUsuario[0]==False:
            return templates.TemplateResponse(
                request=request, 
                name="home.html", 
                context={"pagina":"/login"}
            )
        
        seguidores = session.exec(select(Usuario)
                                  .join(Seguir, Seguir.seguindo_id==usuario.id)
                                  .where(Usuario.id==Seguir.seguidor_id)).all()
        
        posts= session.exec(select(Post).where(Post.usuario_id == usuario.id)).all()
        return templates.TemplateResponse(
            request=request, 
            name="profile.html", 
            context={
                "nome": usuario.username,
                "seguidores":seguidores      
            }
        ) 

@app.get("/logout", response_class=HTMLResponse)
async def sair(request:Request,response: Response):
    response = templates.TemplateResponse(request,"home.html", {"pagina":"/login"})
    response.delete_cookie("session_user")
    return response

    
@app.post("/usuario", response_class=HTMLResponse)
async def criarusuario(username: str =Form(...),senha=Form(...)):
#async def criarUsuario(usuario:Usuario):
    with Session(engine) as session:
        usuario = Usuario(username=username,senha=senha)
        session.add(usuario)
        session.commit()
        session.refresh(usuario)
        return HTMLResponse(content=f"<p>Usuario(a) {usuario.username} criado(a)!</p>")

@app.get("/obras",response_class=HTMLResponse)
async def pagObras(request: Request):
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(
            request,
            "home.html",
            {"pagina": "/obras"})
    with Session(engine) as session:
        obras=session.exec(select(Obra)).all()
    return templates.TemplateResponse(request,
                                      "obras.html",
                                      context={"obras":"/listaObras"}
                                      )

@app.delete("/usuario")
async def DeleteUsuario(username:str):
     with Session(engine) as session:
         usuario = session.exec(select(Usuario).where(Usuario.username == username)).first()
         if not usuario:
             raise HTTPException(404, "Usuário não encontrado")
         session.delete(usuario)
         session.commit()

         return {"ok": True}


@app.get("/obras/{tipo}/{chave}",response_class=HTMLResponse)
async def pagObras(request: Request, tipo:str,chave:str):
    if (not "HX-Request" in request.headers):
        pagina="/obras/"+tipo+"/"+chave
        return templates.TemplateResponse(
            request,
            "home.html",
            {"pagina": pagina})
    with Session(engine) as session:
        obra=session.exec(select(Obra).where(Obra.chave==chave,Obra.tipo==tipo)).first()
        if not obra:
            raise HTTPException(404, " obra não encontrado")
        gostaram=session.exec(select(func.count(Post.reacao)).where(Post.obra_id == obra.id,Post.reacao=="Gostei")).one()
        nGostaram=session.exec(select(func.count(Post.reacao)).where(Post.obra_id == obra.id,Post.reacao=="Odiei")).one()
        visto=session.exec(select(func.count(Post.visto)).where(Post.obra_id == obra.id,Post.visto=="Visto")).one()
        naMeta=session.exec(select(func.count(Post.visto)).where(Post.obra_id == obra.id,Post.visto=="Na meta")).one()
        return templates.TemplateResponse(request,
                                      "obra.html",
                                          context={"obra":obra,
                                                   "visto":visto,
                                                   "gostaram":gostaram,
                                                   "nGostaram":nGostaram,
                                                   "naMeta":naMeta
                                                   }
                                          )
@app.get("/listaObras", response_class=HTMLResponse)
async def lista(request: Request):
    with Session(engine) as session:
        obras=session.exec(select(Obra)).all()
        return templates.TemplateResponse(request, "listaObras.html", {"obras": obras})

@app.post("/obras", response_class=HTMLResponse)
async def registrarObras(
        request:Request,
        nome:str=Form(...),
        tipo:str=Form(...),
        descricao:Optional[str]=Form(None),
        anoLancamento:Optional[int]=Form(None),
        genero1:Optional[str]=Form(None),
        genero2:Optional[str]=Form(None),
        genero3:Optional[str]=Form(None)
):
    with Session(engine) as session:
        obraTeste=session.exec(select(Obra).where(Obra.nome == nome.lower(),Obra.tipo==tipo)).first()
        if not obraTeste:
            chave=nome.replace(" ","")
            chave = chave.lower()
            obra=Obra(
                nome=nome.lower(),
                descricao=descricao,
                chave=chave,
                tipo=tipo,
                anoLancamento=anoLancamento,
                genero1=genero1,
                genero2=genero2,
                genero3=genero3
            )
            
            session.add(obra)
            session.commit()
            session.refresh(obra)
            obras=session.exec(select(Obra)).all()
            return templates.TemplateResponse(request, "listaObras.html", {"obras": obras})
        else:
            raise HTTPException(404, " obra encontrada")

@app.post("/post", response_class=HTMLResponse)
async def postar(
        request:Request,
        obraNome:str=Form(...),
        tipo:str=Form(...),
        meta:Optional[int]=Form(None),
        visto: Optional[str]=Form(...),
        reacao:Optional[str]=Form(None),
        comentarios:Optional[str]=Form(None),
        temUsuario:[bool,str] = Depends(get_active_user)
):
    if temUsuario[0]==True:
        with Session(engine) as session:
            obra = session.exec(select(Obra).where(Obra.nome == obraNome.lower(),Obra.tipo==tipo)).first()
            usuario = session.exec(select(Usuario).where(Usuario.username == temUsuario[1])).first()
            if not usuario:
                raise HTTPException(404, "Usuario não encontrado")
            if not obra:
                chave=obraNome.replace(" ","")
                chave=chave.lower()
                obra=Obra(nome=obraNome.lower(),chave=chave,tipo=tipo)
                session.add(obra)
                session.commit()
                session.refresh(obra)
            post = Post(
                usuario_id=usuario.id,
                obra_id=obra.id,
                visto=visto,
                meta=meta,
                reacao=reacao,
                comentarios=comentarios
            )

            session.add(post)
            session.commit()
            session.refresh(post)
            posts= session.exec(select(Post).where(Post.usuario_id == usuario.id)).all()
            return templates.TemplateResponse(request, "listaObras.html", {"obras": usuario.obras,"posts":posts})
    
    return templates.TemplateResponse(
        request=request, 
        name="home.html", 
        context={"pagina":"/login"}
    )
@app.get("/listaPost", response_class=HTMLResponse)
def lista(request: Request,temUsuario:[bool,str] = Depends(get_active_user)):
    with Session(engine) as session:
        usuario = session.exec(select(Usuario).where(Usuario.username == temUsuario[1])).first()
        if temUsuario[0]==False:
            return templates.TemplateResponse(
                request=request, 
                name="home.html", 
                context={"pagina":"/login"}
            )
        posts= session.exec(select(Post).where(Post.usuario_id == usuario.id)).all()
        return templates.TemplateResponse(request, "listaObras.html", {"obras": usuario.obras,"posts":posts})


@app.put("/post/{tipo}/{chave}",response_class=HTMLResponse)
async def mudarPost(
        request:Request,
        chave:str,
        tipo:str,
        meta:Optional[int]=Form(),
        visto: Optional[str]=Form(...),
        reacao:Optional[str]=Form(...),
        comentarios:Optional[str]=Form(None),
        temUsuario:[bool,str] = Depends(get_active_user)
):
     if temUsuario[0]==True:
        with Session(engine) as session:
            obra = session.exec(select(Obra).where(Obra.chave == chave,Obra.tipo==tipo)).first()
            usuario = session.exec(select(Usuario).where(Usuario.username == temUsuario[1])).first()

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
            session.refresh(post)
            return post
     else:
        return templates.TemplateResponse(
            request=request, 
            name="home.html", 
            context={"pagina":"/login"}
        )

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


@app.post("/seguir")
async def seguir(
        request:Request,
        seguindo_nome:str=Form(...),
        temUsuario:[bool,str] = Depends(get_active_user)
):
    if temUsuario[0]==True:
        with Session(engine) as session:
            seguidor = session.exec(select(Usuario).where(Usuario.username == temUsuario[1])).first()   
            seguindo = session.exec(select(Usuario).where(Usuario.username == seguindo_nome)).first()
            if not seguindo:
                raise HTTPException(404, "Usuário não encontrado")
            seguir=Seguir(
                seguindo=seguindo,
                seguidor=seguidor
            )
            session.add(seguir)
            session.commit()
            session.refresh(seguir)
            
        return
    else:
        return templates.TemplateResponse(
            request=request, 
            name="home.html", 
            context={"pagina":"/login"}
        )
    
@app.get("/seguindo",response_class=HTMLResponse)
async def listaSeguidores(request:Request,temUsuario:[bool,str] = Depends(get_active_user)):
    if temUsuario[0]==True:
        with Session(engine) as session:
            seguindo= session.exec(select(Usuario)
                                  .join(Seguir, Seguir.seguidor_id==usuario.id)
                                  .where(Usuario.id==Seguir.seguindo_id)).all()
            return templates.TemplateResponse(request, "listaSeguindo.html", {"seguindo":seguindo})

@app.delete("/seguir/{user}")
async def pararSeguir(
            user:str,
            temUsuario:[bool,str] = Depends(get_active_user)
):
    if temUsuario[0]==True:
        with Session(engine) as session:
            seguidor = session.exec(select(Usuario).where(Usuario.username == temUsuario[1])).first()   
            seguindo = session.exec(select(Usuario).where(Usuario.username == user)).first()
            if not seguindo:
                raise HTTPException(404, "Usuário não encontrado")
            seguir = session.exec(select(Seguir).where(seguidor.id==seguidor_id,seguindo_id==seguindo.id)).first()
            if not seguir:
                raise HTTPException(404, "Você não seguia ele")
            session.delete(seguir)
            session.commit()
            session.refresh()
            return templates.TemplateResponse(
                request=request, 
                name="home.html", 
                context={"pagina":"/perfil"}
            )
    else:
        return templates.TemplateResponse(
            request=request, 
            name="home.html", 
            context={"pagina":"/login"}
        )
