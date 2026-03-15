from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles

app = FastAPI()
# Monta a pasta "static" na rota "/static"
app.mount("/static", StaticFiles(directory="static"), name="static")
# Sintaxe recomendada: diretório como primeiro argumento posicional
templates = Jinja2Templates(directory="templates")
    
class Usuario(BaseModel):
    nome:str
    senha:str
    bio:str
  
usuarios_db = []





@app.get("/")
async def inicio(request: Request, logado: bool = False):
    if not logado:
        return templates.TemplateResponse(
        request=request, name="formulario.html", context={"logado": False}
    )

@app.post("/usuarios")
def criar_usuario(user: Usuario):
    usuarios_db.append(user)
    return {"usuario": user.nome}


@app.get("/login")
def logue(request: Request, logado: bool = False):
     if not logado:
        return templates.TemplateResponse(
        request=request, name="formulario2.html", context={"logado": False}
    )
     
@app.post("/login")
def login(name: str, password:str, response: Response):
    # Buscamos o usuário usando um laço simples
    usuario_encontrado = None
    for u in usuarios_db:
        if u.nome == name:
            
            if  u.senha==password:
                usuario_encontrado = u
               # raise HTTPException(status_code=404, detail="Senha incorreta")
                break
    
    if not usuario_encontrado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    
    # O servidor diz ao navegador: "Guarde esse nome no cookie 'session_user'"
    response.set_cookie(key="session_user", value=name)
    return {"message": "Logado com sucesso"}




