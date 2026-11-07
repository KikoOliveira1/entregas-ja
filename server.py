@app.post("/api/login/motoboy")
def login_motoboy(dados: LoginSchema):
    nome_digitado = dados.utilizador.strip()
    senha_digitada = dados.senha.strip()

    # Procura ignorando espaços extras e maiúsculas/minúsculas
    motoboy = motoboys_collection.find_one({
        "nome": {"$regex": f"^{nome_digitado.replace(' ', '.*')}$", "$options": "i"}
    })

    if not motoboy:
        raise HTTPException(status_code=401, detail="Utilizador não encontrado.")

    senha_banco = str(motoboy.get("senha", "")).strip()
    if senha_banco and senha_banco != senha_digitada:
        raise HTTPException(status_code=401, detail="Palavra-passe incorreta.")

    return {
        "mensagem": "Login efetuado com sucesso!",
        "motoboy": {
            "id": str(motoboy["_id"]),
            "nome": motoboy.get("nome"),
            "veiculo": motoboy.get("veiculo"),
            "status": motoboy.get("status", "offline")
        }
    }

@app.post("/api/login/comercio")
def login_comercio(dados: LoginSchema):
    nome_digitado = dados.utilizador.strip()
    senha_digitada = dados.senha.strip()

    comercio = comercios_collection.find_one({
        "nome": {"$regex": f"^{nome_digitado.replace(' ', '.*')}$", "$options": "i"}
    })

    if not comercio:
        raise HTTPException(status_code=401, detail="Comércio não encontrado.")

    senha_banco = str(comercio.get("senha", "")).strip()
    if senha_banco and senha_banco != senha_digitada:
        raise HTTPException(status_code=401, detail="Palavra-passe incorreta.")

    return {
        "mensagem": "Login efetuado com sucesso!",
        "comercio": {
            "id": str(comercio["_id"]),
            "nome": comercio.get("nome"),
            "endereco": comercio.get("endereco"),
            "categoria": comercio.get("categoria")
        }
    }
