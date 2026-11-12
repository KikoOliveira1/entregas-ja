import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="Entregas Já API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS DE DADOS ---
class LoginComercioSchema(BaseModel):
    utilizador: str
    senha: str

class StatusMotoboySchema(BaseModel):
    status: str
    motoboy: str | None = "KikoOliveira"
    lat: float | None = None
    lon: float | None = None

class MensagemSchema(BaseModel):
    remetente: str
    texto: str

# --- BANCO EM MEMÓRIA UNIFICADO ---
comercios_db = [
    {
        "utilizador": "lanchonete",
        "senha": "123",
        "comercio": {
            "nome": "Lanchonete Central",
            "categoria": "Alimentação",
            "endereco": "Rua das Flores, 100",
            "lat": -26.1264,
            "lon": -48.6183
        }
    }
]

pedidos_db = [
    {
        "id": "101",
        "comercio": "Lanchonete Central",
        "comercio_nome": "Lanchonete Central",
        "cliente": "Carlos Eduardo",
        "endereco_retirada": "Rua das Flores, 100",
        "endereco_entrega": "Av. Brasil, 500",
        "descricao": "2x X-Salada + 1x Coca-Cola 2L",
        "valor": "12,00",
        "telefone_comercio": "47999999999",
        "status": "pendente",
        "mensagens": []
    }
]

motoboys_db = {
    "KikoOliveira": {
        "id": "1",
        "nome": "KikoOliveira",
        "veiculo": "Start Preta QIL8F44",
        "status": "offline",
        "lat": -26.1264,
        "lon": -48.6183
    }
}

# --- ROTAS DO COMERCIANTE (comercio.html) ---
@app.post("/api/login/comercio")
def login_comercio(dados: LoginComercioSchema):
    for c in comercios_db:
        if c["utilizador"].lower() == dados.utilizador.lower() and c["senha"] == dados.senha:
            return {"sucesso": True, "comercio": c["comercio"]}
    raise HTTPException(status_code=401, detail="Utilizador ou palavra-passe incorretos.")

@app.get("/api/entregas")
def listar_entregas():
    return pedidos_db

@app.post("/api/entregas")
def criar_entrega_comercio(dados: dict):
    novo_id = str(uuid.uuid4())[:6].upper()
    novo_pedido = {
        "id": novo_id,
        "comercio": dados.get("comercio", "Lanchonete Central"),
        "comercio_nome": dados.get("comercio", "Lanchonete Central"),
        "cliente": dados.get("cliente", "Cliente"),
        "endereco_retirada": "Rua das Flores, 100",
        "endereco_entrega": dados.get("endereco_entrega", ""),
        "descricao": dados.get("descricao", ""),
        "valor": dados.get("valor", "10,00"),
        "telefone_comercio": "47999999999",
        "status": "pendente",
        "mensagens": []
    }
    pedidos_db.append(novo_pedido)
    return {"status": "sucesso", "id": novo_id}

@app.delete("/api/entregas/{entrega_id}")
def excluir_entrega(entrega_id: str):
    global pedidos_db
    pedidos_db = [p for p in pedidos_db if p["id"] != entrega_id]
    return {"status": "sucesso"}

@app.get("/api/motoboys/online")
def motoboys_online():
    lista = []
    for nome, dados in motoboys_db.items():
        lista.append({
            "id": dados["id"],
            "nome": dados["nome"],
            "veiculo": dados["veiculo"],
            "status": "online" if dados["status"] in ["disponivel", "em_entrega", "online"] else "offline",
            "lat": dados["lat"],
            "lng": dados["lon"]
        })
    return lista

# --- ROTAS DO MOTOBOY (motoboy.html) ---
@app.get("/api/pedidos/disponiveis")
def obter_pedidos_disponiveis():
    return pedidos_db

@app.post("/api/pedidos/aceitar/{pedido_id}")
def aceitar_pedido(pedido_id: str):
    for p in pedidos_db:
        if p["id"] == pedido_id:
            p["status"] = "aceito"
            return {"status": "sucesso", "message": "Pedido aceito com sucesso!"}
    return {"status": "erro", "message": "Pedido não encontrado"}

@app.post("/api/motoboy/status")
def definir_status_motoboy(dados: StatusMotoboySchema):
    nome = dados.motoboy or "KikoOliveira"
    if nome not in motoboys_db:
        motoboys_db[nome] = {"id": "1", "nome": nome, "veiculo": "Moto", "status": "offline", "lat": -26.1264, "lon": -48.6183}
    
    motoboys_db[nome]["status"] = dados.status
    if dados.lat is not None and dados.lon is not None:
        motoboys_db[nome]["lat"] = dados.lat
        motoboys_db[nome]["lon"] = dados.lon
    return {"status": "sucesso", "mensagem": f"Estado atualizado para: {dados.status}"}

@app.get("/api/motoboy/status")
def obter_status_motoboy():
    return motoboys_db.get("KikoOliveira")

# --- ROTAS DO ADMINISTRADOR & CHAT (admin.html) ---
@app.post("/api/pedidos/{pedido_id}/mensagem")
def enviar_mensagem(pedido_id: str, msg: MensagemSchema):
    for p in pedidos_db:
        if p["id"] == pedido_id:
            p.setdefault("mensagens", []).append({"remetente": msg.remetente, "texto": msg.texto})
            return {"status": "sucesso"}
    return {"status": "erro"}

@app.get("/api/monitoramento/geral")
def monitoramento_geral():
    comercios_mapa = [c["comercio"] for c in comercios_db]
    return {
        "pedidos": pedidos_db,
        "motoboys": motoboys_db,
        "comercios": comercios_mapa
    }

# --- SERVIR ARQUIVOS ESTÁTICOS ---
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)

