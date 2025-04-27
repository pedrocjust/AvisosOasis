import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["discord_bot"]  # Nome do banco que estamos usando

# Coleções específicas
demissoes_collection = db["demissoes"]
ausencias_collection = db["ausencias"]
exoneracoes_collection = db["exoneracoes"]


def save_demissao(data):
    """Salvar uma solicitação de demissão no banco."""
    demissoes_collection.insert_one(data)


def save_ausencia(data):
    """Salvar uma solicitação de ausência no banco."""
    ausencias_collection.insert_one(data)


def save_exoneracao(data):
    """Salvar uma exoneração no banco."""
    exoneracoes_collection.insert_one(data)


def get_demissoes():
    """Pegar todas as demissões."""
    return list(demissoes_collection.find())


def get_ausencias():
    """Pegar todas as ausências."""
    return list(ausencias_collection.find())


def get_exoneracoes():
    """Pegar todas as exonerações."""
    return list(exoneracoes_collection.find())
