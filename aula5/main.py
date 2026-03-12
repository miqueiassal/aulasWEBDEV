from fastapi import FastAPI, Request
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



@app.get("/")
async def inicio(request: Request, logado: bool = False):
    if not logado:
        return templates.TemplateResponse(
        request=request, name="home.html", context={"logado": False}
    )

@app.post("/usuarios")
def criar_usuario(user: Usuario):
    usuarios_db.append(user.dict())
    logado=True
    return {"usuario": user.nome}

