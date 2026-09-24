"""Configurações lidas de variáveis de ambiente (.env)."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = Path(os.getenv("DOCS_DIR", BASE_DIR / "data" / "docs"))
INDEX_DIR = Path(os.getenv("INDEX_DIR", BASE_DIR / "data" / "index"))

OCI_REGION = os.getenv("OCI_REGION", "us-chicago-1")
OCI_COMPARTMENT_ID = os.getenv("OCI_COMPARTMENT_ID", "")
OCI_AUTH = os.getenv("OCI_AUTH", "config_file")  # config_file | instance_principal
OCI_PROFILE = os.getenv("OCI_PROFILE")

CHAT_MODEL = os.getenv("CHAT_MODEL", "command-a-03-2025")
EMBED_MODEL = os.getenv("EMBED_MODEL", "embed-multilingual-v3.0")
TOP_K = int(os.getenv("TOP_K", "6"))
