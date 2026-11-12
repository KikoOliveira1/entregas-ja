from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(
    title="Entregas Já API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos de Dados
class LoginSchema(BaseModel):
    usuario: str | None = None
    senha: str | None = None

class StatusSchema(BaseModel):
    status: str
    motoboy: str | None = None

# Base de dados simulada em memória
pedidos_db = [
    {
        "id": "101",
        "comercio_nome": "Lanchonete Central",
        "endereco_retirada": "Rua das Flores, 100",
        "endereco_entrega": "Av. Brasil, 500",
        "valor": "12,00",
        "telefone_comercio": "47999999999",
        "status": "pendente"
    }
]

status_motoboy_db = {"motoboy": "KikoOliveira", "status": "offline"}

# Rotas da API
@app.post("/api/login/motoboy")
def login_motoboy(dados: LoginSchema | None = None):
    return {
        "sucesso": True,
        "mensagem": "Autenticação efetuada com sucesso",
        "usuario": dados.usuario if dados else None
    }

@app.get("/api/pedidos/disponiveis")
def obter_pedidos():
    return pedidos_db

@app.post("/api/pedidos/criar")
def criar_pedido(pedido: dict):
    pedidos_db.append(pedido)
    return {"status": "sucesso", "message": "Pedido criado e enviado para os motoboys!"}

@app.post("/api/pedidos/aceitar/{pedido_id}")
def aceitar_pedido(pedido_id: str):
    for p in pedidos_db:
        if p["id"] == pedido_id:
            p["status"] = "aceito"
            return {"status": "sucesso", "message": "Pedido aceito com sucesso!"}
    return {"status": "erro", "message": "Pedido não encontrado"}

@app.post("/api/motoboy/status")
def definir_status_motoboy(dados: StatusSchema):
    status_motoboy_db["status"] = dados.status
    status_motoboy_db["motoboy"] = dados.motoboy or "KikoOliveira"
    return {"status": "sucesso", "mensagem": f"Estado atualizado para: {status_motoboy_db['status']}"}

@app.get("/api/motoboy/status")
def obter_status_motoboy():
    return status_motoboy_db

# Serve todos os arquivos HTML da pasta raiz (index.html, motoboy.html, admin.html, etc.)
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
