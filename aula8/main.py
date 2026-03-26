from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory=["Templates", "Templates/Partials"])

likes=0
@app.get("/",response_class=HTMLResponse)
async def home(request: Request):
    
    return templates.TemplateResponse(request, "home.html",{"pagina":"/curtir","curtida": 0})

@app.get("/curtir",response_class=HTMLResponse)
async def FalarCurtidas(request:Request):
    #likes=request.curtidas
    if (not "HX-Request" in request.headers):
        return templates.TemplateResponse(request, "home.html", {"pagina": "/curtir","curtida":1})
    return templates.TemplateResponse(request, "curtidas.html",{"curtida": likes})

@app.post("/curtir", response_class=HTMLResponse)
async def curti(request: Request):
    global likes 
    likes +=1
    return templates.TemplateResponse(request, "home.html",{"curtida": likes, "pagina":"/curtir"})
    

@app.delete("/curtir")
async def descurti(request: Request):
    global likes
    likes=0
    return templates.TemplateResponse(request, "home.html",{"curtida": likes, "pagina":"/curtir"})


