from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent # primeiro parent sobe até pasta fastapi2, segundo parent sobre até pasta projeto
env_path = BASE_DIR / 'fastapi' / '.env'  # vai pegar o .env da pasta fastapi

load_dotenv(dotenv_path = env_path)

DATABASE_URL = os.getenv('DATABASE_URL')

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind = engine) # isso faz com que SessionLocal consiga se conectar à URL correta do banco de dados

Base = declarative_base()